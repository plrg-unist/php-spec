#!/usr/bin/env python3
"""Backed static setter normalization, diagnostic priority and inheritance."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]


def descriptor(setter, final=False, read='PUBLIC'):
    return ['P.COMPLETION = PPCNORMAL', 'P.CLASSES = [pclassdesc]',
            'pclassdesc.PROPERTIES = [ppropertydesc]', 'ppropertydesc.STATIC',
            'ppropertydesc.VISIBILITY = PROPERTY_' + read,
            'ppropertydesc.SETVISIBILITY = ' + setter,
            'ppropertydesc.FINAL = ' + str(final).lower()]


CASES = {
    'static-nullsafe-reference': ('<?php $r=&($o?->c)::f();',
                                 [], 'Cannot take reference of a nullsafe chain'),
    'static-nullsafe-firstclass-reference': ('<?php $r=&($o?->c)::f(...);',
                                            [], 'Cannot take reference of a nullsafe chain'),
    'static-firstclass-reference': ('<?php class A{public static function &get(){static $x=1;return $x;}}$r=&A::get(...);',
                                  [], 'Cannot use result of built-in function in write context'),
    'private-set': ('<?php class A{public private(set) static int $p;}',
                    descriptor('(PROPERTY_PRIVATE)', True), None),
    'omitted-get': ('<?php class A{protected(set) static int $p=1;}',
                    descriptor('(PROPERTY_PROTECTED)'), None),
    'protected-private-set': ('<?php class A{protected private(set) static int $p=1;}',
                              descriptor('(PROPERTY_PRIVATE)', True, 'PROTECTED'), None),
    'equal-public': ('<?php class A{public public(set) static int $p=1;}', descriptor('eps'), None),
    'equal-protected': ('<?php class A{protected protected(set) static int $p=1;}',
                        descriptor('eps', read='PROTECTED'), None),
    'equal-private': ('<?php class A{private private(set) static int $p=1;}',
                      descriptor('eps', read='PRIVATE'), None),
    'explicit-final': ('<?php class A{final public static int $p=1;}', descriptor('eps', True), None),
    'explicit-final-protected': ('<?php class A{final protected static int $p=1;}',
                                 descriptor('eps', True, 'PROTECTED'), None),
    'explicit-final-private': ('<?php class A{final private static int $p=1;}',
                               [], 'Property cannot be both final and private'),
    'final-private-before-type': ('<?php class A{final private static callable $p;}',
                                  [], 'Property cannot be both final and private'),
    'final-private-before-default': ('<?php class A{final private static int $p="bad";}',
                                     [], 'Property cannot be both final and private'),
    'final-private-before-readonly': ('<?php class A{final private static readonly $p;}',
                                      [], 'Property cannot be both final and private'),
    'final-private-before-untyped-set': ('<?php class A{final private private(set) static $p;}',
                                         [], 'Property cannot be both final and private'),
    'equal-public-untyped': ('<?php class A{public public(set) static $p;}', [],
                             'Property with asymmetric visibility A::$p must have type'),
    'equal-protected-untyped': ('<?php class A{protected protected(set) static $p;}', [],
                                'Property with asymmetric visibility A::$p must have type'),
    'equal-private-untyped': ('<?php class A{private private(set) static $p;}', [],
                              'Property with asymmetric visibility A::$p must have type'),
    'untyped-before-weaker-set': ('<?php class A{private public(set) static $p;}', [],
                                 'Property with asymmetric visibility A::$p must have type'),
    'weaker-public-set': ('<?php class A{protected public(set) static int $p=1;}', [],
                          'Visibility of property A::$p must not be weaker than set visibility'),
    'weaker-protected-set': ('<?php class A{private protected(set) static int $p=1;}', [],
                             'Visibility of property A::$p must not be weaker than set visibility'),
    'default-before-set': ('<?php class A{protected public(set) static int $p="bad";}', [],
                           'Cannot use string as default value for property A::$p of type int'),
    'static-readonly': ('<?php class A{public private(set) static readonly int $p;}', [],
                        'Static property A::$p cannot be readonly'),
    'readonly-untyped-before-set': ('<?php class A{public public(set) static readonly $p;}', [],
                                    'Readonly property A::$p must have type'),
    'private-set-final-override': ('<?php class A{public private(set) static int $p=1;}'
                                  'class B extends A{private static string $p="s";}', [],
                                  'Cannot override final property A::$p'),
    'invalid-parent-before-inheritance': ('<?php class A{final private static int $p=1;}'
                                          'class B extends A{public int $p=2;}', [],
                                          'Property cannot be both final and private'),
    'explicit-final-override': ('<?php class A{final protected static int $p=1;}'
                                'class B extends A{private string $p="s";}', [],
                                'Cannot override final property A::$p'),
    'equal-private-independent': ('<?php class A{private private(set) static int $p=1;}'
                                  'class B extends A{public static string $p="s";}',
                                  ['P.COMPLETION = PPCNORMAL'], None),
    'set-narrowing-omitted': ('<?php class A{public static int $p=1;}'
                             'class B extends A{public protected(set) static int $p=2;}', [],
                             'Set access level of B::$p must be omitted (as in class A)'),
    'set-narrowing-protected': ('<?php class A{public protected(set) static int $p=1;}'
                               'class B extends A{public private(set) static int $p=2;}', [],
                               'Set access level of B::$p must be protected(set) (as in class A) or weaker'),
    'set-before-get-and-type': ('<?php class A{public static int $p=1;}'
                               'class B extends A{protected private(set) static string $p="s";}', [],
                               'Set access level of B::$p must be omitted (as in class A)'),
    'static-before-set': ('<?php class A{public int $p=1;}'
                          'class B extends A{public private(set) static int $p=2;}', [],
                          'Cannot redeclare non static A::$p as static B::$p'),
    'set-omission-widens': ('<?php class A{public protected(set) static int $p=1;}'
                            'class B extends A{public static int $p=2;}',
                            ['P.COMPLETION = PPCNORMAL'], None),
    'equal-child-widens': ('<?php class A{public protected(set) static int $p=1;}'
                           'class B extends A{public public(set) static int $p=2;}',
                           ['P.COMPLETION = PPCNORMAL'], None),
    'parent-read-permits-child-set': ('<?php class A{protected static int $p=1;}'
                                     'class B extends A{public protected(set) static int $p=2;}',
                                     ['P.COMPLETION = PPCNORMAL'], None),
    'deferred-final-link': ('<?php if(true){class A{public private(set) static int $p=1;}}'
                            'class B extends A{public static int $p=2;}',
                            ['P.COMPLETION = PPCNORMAL', 'P.CLASSES = [pclassdesc_a,pclassdesc_b]',
                             '~pclassdesc_a.EARLY', '~pclassdesc_b.EARLY'], None),
    'ordinary-instance-shape': ('<?php class A{protected int $p=1;}',
                                ['P.COMPLETION = PPCNORMAL', 'P.CLASSES = [pclassdesc]',
                                 'pclassdesc.PROPERTIES = [ppropertydesc]', '~ppropertydesc.STATIC',
                                 'ppropertydesc.SETVISIBILITY = eps', '~ppropertydesc.FINAL'], None),
    'internal-throwable-shape': ('<?php',
                               ['$throwable_layout("Exception") = [ppropertydesc_a,ppropertydesc_b,ppropertydesc_c,ppropertydesc_d,ppropertydesc_e,ppropertydesc_f,ppropertydesc_g]',
                                *[check for label in 'abcdefg' for check in
                                  ('ppropertydesc_' + label + '.SETVISIBILITY = eps',
                                   '~ppropertydesc_' + label + '.FINAL')]], None),
    'instance-set-still-unsupported': ('<?php class A{public private(set) int $p=1;}',
                                     ['P.COMPLETION = PPCABRUPT (UNSUPPORTED "property visibility, static, readonly, or final")'], 'unsupported'),
    'instance-readonly-still-unsupported': ('<?php class A{public readonly int $p;}',
                                          ['P.COMPLETION = PPCABRUPT (UNSUPPORTED "property visibility, static, readonly, or final")'], 'unsupported'),
    'multiline-group-error': ('<?php\nclass A{\nfinal private static int\n$p=1;\n}', [],
                              'Property cannot be both final and private'),
    'multiline-inheritance-error': ('<?php\nclass A{public protected(set) static int $p=1;}\n\n'
                                    'class B extends A{\npublic private(set) static int $p=2;\n}', [],
                                    'Set access level of B::$p must be protected(set) (as in class A) or weaker'),
    'source-descriptor-authentication': ('<?php class A{public private(set) static int $p=1;}',
                                       ['P.COMPLETION = PPCNORMAL', 'S = SOURCE_INITIAL',
                                        'S.CLASSES = [pclassdesc]',
                                        'pclassdesc.PROPERTIES = [ppropertydesc]',
                                        'ppropertydesc.SETVISIBILITY = (PROPERTY_PRIVATE)',
                                        'ppropertydesc.FINAL', '$class_state_valid(S)',
                                        '~$class_state_valid(S[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc[.SETVISIBILITY = (PROPERTY_PROTECTED)]]]]])',
                                        '~$class_state_valid(S[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc[.SETVISIBILITY = eps]]]]])',
                                        '~$class_state_valid(S[.CLASSES = [pclassdesc[.PROPERTIES = [ppropertydesc[.FINAL = false]]]]])'], None),
    'late-final-rejection': ('<?php echo "P";if(true){class A{public private(set) static int $p=1;}}'
                             'echo "Q";class B extends A{private static string $p="s";}',
                             ['P.COMPLETION = PPCNORMAL', 'S_initial = SOURCE_INITIAL',
                              'S = $drive(S_initial[.COMPLETION = NORMAL],512)',
                              'S.COMPLETION = FATAL ($ptascii("Cannot override final property A::$p")) 1',
                              'S.EVENTS = [OUTPUT ([80]),OUTPUT ([81])]', 'S.CLASSES = [pclassdesc_a,pclassdesc_b]',
                              'pclassdesc_a.PROPERTIES = [ppropertydesc]',
                              'S.CLASSNAMES = [($ptascii("a"),pclassdesc_a.ORIGIN)]',
                              'S.LINKEDPARENTS = eps', 'S.CLASSSTATICS = [pclassstatic]',
                              'pclassstatic.DECL = ppropertydesc.ORIGIN',
                              'pclassstatic.STATE = PROP_VALUE (DIRECT (PINT 1))',
                              '$class_state_valid(S)', '$heap_valid($heap_graph(S))'], None),
    'late-set-narrowing': ('<?php echo "P";if(true){class A{public protected(set) static int $p=1;}}'
                           'echo "Q";class B extends A{public private(set) static int $p=2;}',
                           ['P.COMPLETION = PPCNORMAL', 'S_initial = SOURCE_INITIAL',
                            'S = $drive(S_initial[.COMPLETION = NORMAL],512)',
                            'S.COMPLETION = FATAL ($ptascii("Set access level of B::$p must be protected(set) (as in class A) or weaker")) 1',
                            'S.EVENTS = [OUTPUT ([80]),OUTPUT ([81])]', 'S.CLASSES = [pclassdesc_a,pclassdesc_b]',
                            'pclassdesc_a.PROPERTIES = [ppropertydesc]',
                            'S.CLASSNAMES = [($ptascii("a"),pclassdesc_a.ORIGIN)]',
                            'S.LINKEDPARENTS = eps', 'S.CLASSSTATICS = [pclassstatic]',
                            'pclassstatic.DECL = ppropertydesc.ORIGIN',
                            'pclassstatic.STATE = PROP_VALUE (DIRECT (PINT 1))',
                            '$class_state_valid(S)', '$heap_valid($heap_graph(S))'], None),
}

ERROR_LINES = {'multiline-group-error': 3, 'multiline-inheritance-error': 4}
RUNTIME_ERRORS = {'late-final-rejection': 'Cannot override final property A::$p',
                  'late-set-narrowing': 'Set access level of B::$p must be protected(set) (as in class A) or weaker'}
INHERITANCE_CASES = {
    'private-set-final-override', 'explicit-final-override', 'equal-private-independent',
    'set-narrowing-omitted', 'set-narrowing-protected', 'set-before-get-and-type',
    'static-before-set', 'set-omission-widens', 'equal-child-widens',
    'parent-read-permits-child-set', 'deferred-final-link', 'multiline-inheritance-error',
}


def fixture_lines(name, checked, path):
    _, checks, message = CASES[name]
    initial = '$php_run(program_source,0,' + json.dumps(base64.b64encode(os.fsencode(path)).decode()) + ')'
    lines = ['program_source = ' + checked['fixture'],
             'P = $ppstart(91, program_source, $ptascii(' + json.dumps(str(path)) + '))',
             *[check.replace('SOURCE_INITIAL', initial) for check in checks]]
    if name in INHERITANCE_CASES:
        if not checks:
            lines.append('P.COMPLETION = PPCNORMAL')
        lines.append('S_link = $compile_source($initial_state(NORMAL)[.FILES = [SOURCEFILE 91 ($ptascii('
                     + json.dumps(str(path)) + '))]], P)')
        if message is None:
            lines.append('S_link.COMPLETION = NORMAL')
        else:
            lines.append('S_link.COMPLETION = FATAL ($ptascii(' + json.dumps(message) + ')) '
                         + str(ERROR_LINES.get(name, 1)))
    elif name in ['static-firstclass-reference', 'static-nullsafe-reference',
                  'static-nullsafe-firstclass-reference']:
        lines.append('P.COMPLETION = PPCABRUPT (STATICERROR ' + json.dumps(message) + ' 1)')
    elif message not in (None, 'unsupported'):
        lines.append('P.COMPLETION = PPCABRUPT (STATICBYTES $ptascii(' + json.dumps(message) + ') ' + str(ERROR_LINES.get(name, 1)) + ')')
    return lines


def main():
    from static_set_access import inputs, sha
    import typed_static_invoke_set_protocol as driver
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare-only', action='store_true',
                        help='Check ASTs and elaborate unused fixture bodies; no original native or model-state execution')
    parser.add_argument('--select', help='Comma-separated case IDs')
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(selected) == len(set(selected)) and all(name in CASES for name in selected)
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = inputs()
    modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    out = Path(tempfile.mkdtemp(prefix='static-set-compiler-', dir=ROOT / '.tools'))
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    report = {'result': 'fail', 'selected': selected, 'records': [], 'inputs': before,
              'profile': profile, 'cwd': str(ROOT), 'mode': 'unused-body-elaboration' if args.prepare_only else 'compiler-contracts',
              'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'state_assertions_evaluated': 0, 'unused_body_assertions': 0}
    frontend = adapter = None
    unused = []
    print(out, flush=True)
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
            'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for name in selected:
            source, _, message = CASES[name]
            directory = out / name; directory.mkdir()
            path = directory / 'source.php'; path.write_text(source)
            row = {'id': name, 'source_sha256': sha(path), 'completed': False,
                   'scope': 'unsupported-control' if message == 'unsupported' else 'compiler-contract'}
            report['records'].append(row)
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(path.read_bytes()).decode()})
            assert parsed['accepted'] is True, (name, parsed)
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            lines = fixture_lines(name, checked, path)
            (directory / 'assertions.json').write_text(json.dumps(lines, indent=2) + '\n')
            body = 'dec $body() : bool\ndef $body() = true\n' + ''.join('  -- if ' + line + '\n' for line in lines)
            fixture = directory / 'protocol.watsup'
            fixture.write_text(body + '\ndec $main() : bool\ndef $main() = $body()\n')
            row.update(assertions=len(lines), fixture_sha256=sha(fixture))
            if args.prepare_only:
                unused.append(body.replace('$body', '$unused_' + str(len(unused))))
                report['unused_body_assertions'] += len(lines)
            else:
                native = driver.process([str(ROOT / '.tools/php/bin/php'), '-n', *flags,
                    *([] if name in RUNTIME_ERRORS else ['-l']), str(path)], directory / 'native', 30, ROOT)
                if name in RUNTIME_ERRORS:
                    diagnostic = ('Fatal error: ' + RUNTIME_ERRORS[name] + ' in ' + str(path) + ' on line 1\nStack trace:\n#0 {main}\n').encode()
                    assert native.returncode == 255 and native.stdout == b'PQ' and native.stderr == diagnostic
                elif message not in (None, 'unsupported'):
                    diagnostic = ('Fatal error: ' + message + ' in ' + str(path) + ' on line ' + str(ERROR_LINES.get(name, 1)) + '\nStack trace:\n#0 {main}\n').encode()
                    assert native.returncode == 255 and native.stderr == diagnostic
                    assert native.stdout == ('Errors parsing ' + str(path) + '\n').encode()
                else:
                    assert native.returncode == 0 and not native.stderr
                    assert native.stdout == ('No syntax errors detected in ' + str(path) + '\n').encode()
                result = driver.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                    *modules, str(fixture)], directory / 'numeric', 120, ROOT)
                assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
                row.update(native_phase='late-runtime-link' if name in RUNTIME_ERRORS else 'lint-compilation', passed=True)
                report['state_assertions_evaluated'] += len(lines)
            row['completed'] = True
            print(name, 'prepared' if args.prepare_only else 'pass', len(lines), flush=True)
        if args.prepare_only:
            fixture = out / 'all-unused.watsup'
            fixture.write_text('\n'.join(unused) + '\ndec $main() : bool\ndef $main() = true\n')
            result = driver.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                *modules, str(fixture)], out / 'unused-numeric', 120, ROOT)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report['elaboration'] = {'completed': True, 'state_assertions_evaluated': 0, 'fixture_sha256': sha(fixture)}
        report['result'] = 'prepared' if args.prepare_only else 'pass'
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        cleanup = []
        for worker in [adapter, frontend]:
            if worker is not None:
                try:
                    worker.close()
                except BaseException as error:
                    cleanup.append({'type': type(error).__name__, 'message': str(error)})
        report['cleanup_errors'] = cleanup
        report['after_inputs'] = inputs()
        if cleanup or report['after_inputs'] != before:
            report['result'] = 'fail'
        report['raw_files'] = {str(p.relative_to(ROOT)): {'sha256': sha(p), 'bytes': p.stat().st_size,
            'mode': oct(p.stat().st_mode & 0o7777)} for p in sorted(out.rglob('*')) if p.is_file()}
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['result'], flush=True)
    assert report['result'] == ('prepared' if args.prepare_only else 'pass')


if __name__ == '__main__':
    main()
