#!/usr/bin/env python3
"""Fresh source-unit append and observer filename provenance."""
import base64
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = Path(tempfile.mkdtemp(prefix='dynamic-source-registry-', dir=ROOT / '.tools'))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    inputs = [*modules, ROOT / 'spec/semantics/modules.json', runner,
              ROOT / '_build/default/adapter/main.exe',
              ROOT / 'frontend/worker.php', ROOT / '.tools/php/bin/php',
              ROOT / '.tools/php-file.so', ROOT / 'bin/php-semantics', Path(__file__)]
    before = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    sources = [b'<?php namespace N; use DateTime as D; '
               b'function f(){} class C{} $x=1; echo "M";',
               b'<?php $y=2; echo "E";', b'<?php break;',
               b'<?php goto missing;', b'<?php echo 1; namespace N;',
               b'<?php $y=2; echo "E";',
               b'<?php namespace N; function f(){}',
               b'<?php namespace N; class C{}',
               b'<?php declare(strict_types=1); echo "S";']
    files = [b'/tmp/dynamic-registry-main.php', b'/tmp/dynamic-registry-eval.php',
             b'/tmp/dynamic-registry-error.php', b'/tmp/dynamic-registry-goto.php',
             b'/tmp/dynamic-registry-namespace.php', b'/tmp/dynamic-registry-repeat.php',
             b'/tmp/dynamic-registry-function.php', b'/tmp/dynamic-registry-class.php',
             b'/tmp/dynamic-registry-strict.php']
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                     out / 'adapter')
    fixtures = []
    try:
        for index, source in enumerate(sources):
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            if index == 4:
                assert not parsed['accepted'] and parsed['category'] == 'parser_rejection'
                parts = []
                for part in (b'<?php echo 1;', b'<?php namespace N;'):
                    fragment = frontend.request({'op': 'parse',
                                                 'source': base64.b64encode(part).decode()})
                    assert fragment['accepted'], fragment
                    parts.append(fragment['ast']['program'][0])
                ast = {'version': 1, 'program': parts}
            else:
                assert parsed['accepted'], (index, parsed)
                ast = parsed['ast']
            checked = adapter.request({'op': 'check', 'ast': ast, 'fixture': True})
            fixtures.append(checked['fixture'])
    finally:
        frontend.close()
        adapter.close()

    b64 = lambda data: json.dumps(base64.b64encode(data).decode())
    checks = [
        f'P_main = $ppstart(0, {fixtures[0]}, $base64({b64(files[0])}))',
        f'P_eval = $ppstart(1, {fixtures[1]}, $base64({b64(files[1])}))',
        f'P_error = $ppstart(2, {fixtures[2]}, $base64({b64(files[2])}))',
        f'P_goto = $ppstart(3, {fixtures[3]}, $base64({b64(files[3])}))',
        f'P_namespace = $ppstart(4, {fixtures[4]}, $base64({b64(files[4])}))',
        f'P_repeat = $ppstart(5, {fixtures[5]}, $base64({b64(files[5])}))',
        f'P_dupfunc = $ppstart(6, {fixtures[6]}, $base64({b64(files[6])}))',
        f'P_dupclass = $ppstart(7, {fixtures[7]}, $base64({b64(files[7])}))',
        f'P_strict = $ppstart(8, {fixtures[8]}, $base64({b64(files[8])}))',
        'P_main.COMPLETION = PPCNORMAL',
        'P_eval.COMPLETION = PPCNORMAL',
        'P_dupfunc.COMPLETION = PPCNORMAL',
        'P_dupclass.COMPLETION = PPCNORMAL',
        'P_strict.ENV.STRICT',
        '~P_eval.ENV.STRICT',
        'P_main.ENV.NAMESPACE = $ptascii("N")',
        'P_eval.ENV.NAMESPACE = eps',
        'P_main.ENV.CLASSES =/= eps',
        'P_eval.ENV.CLASSES = eps',
        'P_main.CVS =/= P_eval.CVS',
        f'Q = {{ ENV eps, ARGV ([{list(files[0])}]), '
        f'FILE ({list(files[0])}), SECONDS 0, MICROSECONDS 0, '
        'VARIABLES ([69,71,80,67,83]), JIT true, CWD eps }',
        '$request_valid(Q)',
        'S_main = $compile_source($request_bootstrap($initial_state(NORMAL)[.FILES = '
        f'[SOURCEFILE 0 $base64({b64(files[0])})]], Q), P_main)',
        'S_main.COMPLETION = NORMAL',
        '$compile_source_append($initial_state(NORMAL)[.FILES = S_main.FILES], P_main).COMPLETION = '
        'UNSUPPORTED "invalid dynamic source registration"',
        'S_main.CVS = P_main.CVS',
        'S_main.CVS =/= eps',
        'S_main.SYMBOLS =/= eps',
        'S_main.STORE =/= eps',
        'S_main.REQUEST = (Q)',
        'S_main.FUNCTIONS =/= eps',
        'S_main.CLASSES =/= eps',
        f'S_base = S_main[.FILES = S_main.FILES ++ [SOURCEFILE 1 $base64({b64(files[1])})]]'
        '[.EVENTS = S_main.EVENTS ++ [OUTPUT ([112,114,105,111,114])]]',
        'S_eval = $compile_source_append(S_base, P_eval)',
        'S_eval.COMPLETION = NORMAL',
        'S_eval.EVENTS = S_base.EVENTS',
        '$source_unit(S_eval.SOURCES, 1) = (pcunit_eval)',
        'S_eval.SOURCES = S_main.SOURCES ++ [pcunit_eval]',
        'pcunit_eval.ID = 1',
        '$pool_at(S_eval.POOLS, 1) = (ppool_eval)',
        'S_eval.POOLS = S_main.POOLS ++ [ppool_eval]',
        'ppool_eval.UNIT = 1',
        '$code_at(S_eval.CODE, 1) = (pcode_eval)',
        'S_eval.CODE = S_main.CODE ++ [pcode_eval]',
        'pcode_eval.UNIT = 1',
        'S_eval.TODO = S_main.TODO',
        'S_eval.CVS = S_main.CVS',
        'S_eval.SYMBOLS = S_main.SYMBOLS',
        'S_eval.REQUEST = S_main.REQUEST',
        'S_eval.ENV = S_main.ENV',
        'S_eval.STORE = S_main.STORE',
        'S_eval.RESULT = S_main.RESULT',
        'S_eval.FILES = S_base.FILES',
        'P_repeat.FOLD.SOURCE.AST = P_eval.FOLD.SOURCE.AST',
        f'S_repeatbase = S_eval[.FILES = S_eval.FILES ++ [SOURCEFILE 5 $base64({b64(files[5])})]]',
        'S_repeat = $compile_source_append(S_repeatbase, P_repeat)',
        '$source_unit(S_repeat.SOURCES, 5) = (pcunit_repeat)',
        '$pool_at(S_repeat.POOLS, 5) = (ppool_repeat)',
        '$code_at(S_repeat.CODE, 5) = (pcode_repeat)',
        'S_repeat.SOURCES = S_eval.SOURCES ++ [pcunit_repeat]',
        'S_repeat.POOLS = S_eval.POOLS ++ [ppool_repeat]',
        'S_repeat.CODE = S_eval.CODE ++ [pcode_repeat]',
        'S_repeat.TODO = S_eval.TODO',
        'S_repeat.COMPLETION = NORMAL',
        f'S_strictbase = S_eval[.FILES = S_eval.FILES ++ [SOURCEFILE 8 $base64({b64(files[8])})]]',
        'S_strict = $compile_source_append(S_strictbase, P_strict)',
        '$code_at(S_strict.CODE, 8) = (pcode_strict)',
        'pcode_strict.STRICT',
        'S_strict.CVS = S_eval.CVS',
        'S_strict.TODO = S_eval.TODO',
        f'S_dupfuncbase = S_eval[.FILES = S_eval.FILES ++ [SOURCEFILE 6 $base64({b64(files[6])})]]',
        'S_dupfunc = $compile_source_append(S_dupfuncbase, P_dupfunc)',
        '$source_unit(S_dupfunc.SOURCES, 6) = (pcunit_dupfunc)',
        'S_dupfunc.SOURCES = S_eval.SOURCES ++ [pcunit_dupfunc]',
        'S_dupfunc.COMPLETION = FATAL ptbytes_dupfunc z_dupfunc',
        'S_dupfunc.ERRORORIGIN = (PORIGIN 6 eps)',
        'S_dupfunc.TODO = S_eval.TODO',
        'S_dupfunc.CVS = S_eval.CVS',
        'S_dupfunc.REQUEST = S_eval.REQUEST',
        f'S_dupclassbase = S_eval[.FILES = S_eval.FILES ++ [SOURCEFILE 7 $base64({b64(files[7])})]]',
        'S_dupclass = $compile_source_append(S_dupclassbase, P_dupclass)',
        '$source_unit(S_dupclass.SOURCES, 7) = (pcunit_dupclass)',
        'S_dupclass.SOURCES = S_eval.SOURCES ++ [pcunit_dupclass]',
        'S_dupclass.COMPLETION = FATAL ptbytes_dupclass z_dupclass',
        'S_dupclass.ERRORORIGIN = (PORIGIN 7 eps)',
        'S_dupclass.TODO = S_eval.TODO',
        'S_dupclass.CVS = S_eval.CVS',
        'S_dupclass.REQUEST = S_eval.REQUEST',
        '$compile_source_append(S_eval, P_eval).COMPLETION = UNSUPPORTED "invalid dynamic source registration"',
        '$compile_source_append(S_main, P_eval).COMPLETION = UNSUPPORTED "invalid dynamic source registration"',
        '$compile_source_append(S_base[.FILES = S_base.FILES ++ '
        '[SOURCEFILE 1 $ptascii("duplicate.php")]], P_eval).COMPLETION = '
        'UNSUPPORTED "invalid dynamic source registration"',
        '$compile_source_append(S_base, P_eval[.LOCATION.UNIT = 99]).COMPLETION = '
        'UNSUPPORTED "invalid dynamic source registration"',
        '$compile_source_append(S_base, P_eval[.LOCATION.FILE = $ptascii("wrong.php")]).COMPLETION = '
        'UNSUPPORTED "invalid dynamic source registration"',
        '$compile_source_append(S_base, P_eval[.FOLD.FILE = ($ptascii("wrong.php"))]).COMPLETION = '
        'UNSUPPORTED "invalid dynamic source registration"',
        '$compile_source_append(S_main[.FILES = S_main.FILES ++ '
        '[SOURCEFILE 1 $ptascii("wrong.php")]], P_eval).COMPLETION = '
        'UNSUPPORTED "invalid dynamic source registration"',
        f'S_badbase = S_eval[.FILES = S_eval.FILES ++ [SOURCEFILE 2 $base64({b64(files[2])})]]',
        'S_bad = $compile_source_append(S_badbase, P_error)',
        '$source_unit(S_bad.SOURCES, 2) = (pcunit_error)',
        'S_bad.SOURCES = S_eval.SOURCES ++ [pcunit_error]',
        'pcunit_error.ID = 2',
        'S_bad.CODE = S_eval.CODE',
        'S_bad.POOLS = S_eval.POOLS',
        'S_bad.TODO = S_eval.TODO',
        'S_bad.CVS = S_eval.CVS',
        'S_bad.SYMBOLS = S_eval.SYMBOLS',
        'S_bad.REQUEST = S_eval.REQUEST',
        'S_bad.ALLOCATIONS = S_eval.ALLOCATIONS',
        'S_bad.ENV = S_eval.ENV',
        'S_bad.STORE = S_eval.STORE',
        'S_bad.EVENTS = S_eval.EVENTS',
        'S_bad.COMPLETION = STATICBYTES ptbytes_error z_error',
        'S_bad.ERRORORIGIN = (PORIGIN 2 eps)',
        f'S_gotobase = S_eval[.FILES = S_eval.FILES ++ [SOURCEFILE 3 $base64({b64(files[3])})]]',
        'S_goto = $compile_source_append(S_gotobase, P_goto)',
        '$source_unit(S_goto.SOURCES, 3) = (pcunit_goto)',
        'S_goto.SOURCES = S_eval.SOURCES ++ [pcunit_goto]',
        'pcunit_goto.ID = 3',
        'S_goto.CODE = S_eval.CODE',
        'S_goto.POOLS = S_eval.POOLS',
        'S_goto.TODO = S_eval.TODO',
        'S_goto.REQUEST = S_eval.REQUEST',
        'S_goto.STORE = S_eval.STORE',
        'S_goto.COMPLETION = STATICBYTES ptbytes_goto z_goto',
        'S_goto.ERRORORIGIN = (PORIGIN 3 eps)',
        'P_namespace.COMPLETION = PPCNAMESPACE',
        f'S_namespacebase = S_eval[.FILES = S_eval.FILES ++ [SOURCEFILE 4 $base64({b64(files[4])})]]',
        'S_namespace = $compile_source_append(S_namespacebase, P_namespace)',
        '$source_unit(S_namespace.SOURCES, 4) = (pcunit_namespace)',
        'S_namespace.SOURCES = S_eval.SOURCES ++ [pcunit_namespace]',
        'S_namespace.CODE = S_eval.CODE',
        'S_namespace.POOLS = S_eval.POOLS',
        'S_namespace.TODO = S_eval.TODO',
        'S_namespace.COMPLETION = STATICBYTES ptbytes_namespace z_namespace',
        'S_namespace.ERRORORIGIN = (PORIGIN 4 eps)',
        f'P_mainbad = $ppstart(0, {fixtures[2]}, $base64({b64(files[0])}))',
        'S_mainbad = $compile_source($request_bootstrap($initial_state(NORMAL)[.FILES = '
        f'[SOURCEFILE 0 $base64({b64(files[0])})]], Q), P_mainbad)',
        'S_mainbad.COMPLETION = STATICBYTES ptbytes_main z_main',
        'S_mainbad.ERRORORIGIN = eps',
        'pllocation_eval = P_eval.LOCATION[.LINE = 7]',
        'S_diag = $compiler_diagnostics(S_eval, [PLDIAGNOSTIC "warning" '
        '"continue-switch" ([$ptascii("message")]) pllocation_eval])',
        'S_diag.EVENTS = S_eval.EVENTS ++ [DIAGNOSTIC_SOURCE 1 "Warning" '
        '$ptascii("message") 7]',
        'S_fatal = $compiler_diagnostics(S_eval, [PLDIAGNOSTIC "fatal" '
        '"function-message" ([$ptascii("bad")]) pllocation_eval])',
        'S_fatal.COMPLETION = STATICBYTES $ptascii("bad") 7',
        'S_fatal.ERRORORIGIN = (PORIGIN 1 eps)',
        'S_warn = $report_event(S_eval[.ORIGIN = (PORIGIN 1 eps)], '
        'WARNING $ptascii("v") 8, 2)',
        'S_warn.EVENTS = S_eval.EVENTS ++ [WARNING_SOURCE 1 $ptascii("v") 8]',
        'S_main_warn = $report_event(S_main[.ORIGIN = (PORIGIN 0 eps)], '
        'WARNING $ptascii("m") 3, 2)',
        'S_main_warn.EVENTS = S_main.EVENTS ++ [WARNING $ptascii("m") 3]',
    ]
    fixture = out / 'registry.watsup'
    fixture.write_text('dec $main() : bool\ndef $main() = true\n' +
                       ''.join('  -- if ' + check + '\n' for check in checks))
    command = [str(runner), *map(str, modules), str(fixture)]
    result = subprocess.run(command, capture_output=True, timeout=180)
    (out / 'stdout').write_bytes(result.stdout)
    (out / 'stderr').write_bytes(result.stderr)
    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr

    observe = runpy.run_path(str(ROOT / 'bin/php-semantics'))['observe']
    sourcefiles = [{'args': [i, list(name)]} for i, name in enumerate(files)]
    state = {'FILES': sourcefiles, 'EVENTS': [
        {'tag': 'WARNING_SOURCE', 'args': [1, list(b'v'), 8]},
        {'tag': 'DIAGNOSTIC_SOURCE', 'args': [2, 'Warning', list(b'nested'), 9]}],
        'COMPLETION': {'tag': 'NORMAL', 'args': []}, 'TRACE': []}
    observed = observe(state, files[0].decode())
    assert base64.b64decode(observed['stderr']) == (
        b'Warning: Undefined variable $v in ' + files[1] + b' on line 8\n'
        b'Warning: nested in ' + files[2] + b' on line 9\n')
    state['COMPLETION'] = {'tag': 'STATICBYTES', 'args': [list(b'bad'), 7]}
    state['ERRORORIGIN'] = {'args': [2, []]}
    assert files[2] in base64.b64decode(observe(state, files[0].decode())['stderr'])
    state['COMPLETION'] = {'tag': 'FATAL', 'args': [list(b'duplicate'), 1]}
    state['ERRORORIGIN'] = {'args': [7, []]}
    assert files[7] in base64.b64decode(observe(state, files[0].decode())['stderr'])
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    report = {'result': 'pass', 'assertions': len(checks) + 3,
              'inputs': before, 'source_sha256': [hashlib.sha256(s).hexdigest() for s in sources],
              'fixture_sha256': digest(fixture), 'observer_files': [name.decode() for name in files],
              'synthetic_typed_ast_case': 'P_namespace combines separately parsed nodes to test an otherwise helper-rejected PPCNAMESPACE internal route'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'], report['assertions'])


if __name__ == '__main__':
    main()
