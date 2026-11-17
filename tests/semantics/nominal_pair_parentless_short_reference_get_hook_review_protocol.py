#!/usr/bin/env python3
"""Independent two-class order, namespace and malformed-header counterexamples."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import scoped_class_parentless_short_reference_get_hook_review_protocol as names
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
HELPER = '$hook_short_reference_nominal_pair_header'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def union(*members):
    return 'NUnionType (SEQUENCE ([' + ','.join(members) + '])) eps'


def branches(*classes):
    return '[' + ','.join('(PTBRANCH ([PTCLASS ' + names.value(name) + ']))' for name in classes) + ']'


def assertions():
    rows = []

    def check(label, ast, normalized, lexical, expected):
        rows.append({'id': label, 'expected': expected, 'premise': ('' if expected else '~') +
                     HELPER + '(' + ast + ',' + normalized + ',' + lexical + ')'})

    plain = names.context(namespace=b'Def333', file=b'original333.php')
    imported = names.context(namespace=b'Def333', file=b'original333.php',
                             imports=((b'Lead', b'Payload333\\First'), (b'Tree', b'Payload333')))
    choices = []
    for left_kind in ('NName', 'NNameRelative', 'NNameFullyQualified'):
        for right_kind in ('NName', 'NNameRelative', 'NNameFullyQualified'):
            left = b'First' if left_kind == 'NNameFullyQualified' else b'Def333\\First'
            right = b'Second' if right_kind == 'NNameFullyQualified' else b'Def333\\Second'
            choices.append((left_kind + '-' + right_kind, b'First', left_kind, left,
                            b'Second', right_kind, right, plain))
    choices += [
        ('alias-prefix', b'lEaD', 'NName', b'Payload333\\First',
         b'tReE\\Second', 'NName', b'Payload333\\Second', imported),
        ('relative-bypasses-alias', b'Lead', 'NNameRelative', b'Def333\\Lead',
         b'Tree\\Second', 'NName', b'Payload333\\Second', imported),
        ('qualified-ordinary', b'Nested\\First', 'NName', b'Def333\\Nested\\First',
         b'Second', 'NNameRelative', b'Def333\\Second', plain),
        ('relative-confusable-quiet', b'boolean', 'NNameRelative', b'Def333\\boolean',
         b'Second', 'NName', b'Def333\\Second', plain),
        ('fq-confusable-quiet', b'boolean', 'NNameFullyQualified', b'boolean',
         b'Second', 'NName', b'Def333\\Second', plain),
        ('nested-underscore-quiet', b'Nested\\_', 'NName', b'Def333\\Nested\\_',
         b'Second', 'NName', b'Def333\\Second', plain),
        ('high-byte', b'\x80First', 'NName', b'Def333\\\x80First',
         b'Second', 'NNameRelative', b'Def333\\Second', plain),
    ]
    for label, left, left_kind, resolved_left, right, right_kind, resolved_right, lexical in choices:
        raw_left, raw_right = names.raw(left, left_kind), names.raw(right, right_kind)
        ast = union(raw_left, raw_right)
        normalized = branches(resolved_left, resolved_right)
        check(label, ast, normalized, lexical, True)
        check(label + '-raw-reversed', union(raw_right, raw_left), normalized, lexical, False)
        check(label + '-normalized-reversed', ast, branches(resolved_right, resolved_left), lexical, False)
        check(label + '-left-bytes', ast, branches(resolved_left + b'X', resolved_right), lexical, False)
        check(label + '-right-bytes', ast, branches(resolved_left, resolved_right + b'X'), lexical, False)
        check(label + '-left-case', ast, branches(resolved_left.swapcase(), resolved_right), lexical, False)
        check(label + '-right-case', ast, branches(resolved_left, resolved_right.swapcase()), lexical, False)
        check(label + '-old-one-class-many-builtins', ast, normalized, lexical, False)
        rows[-1]['premise'] = rows[-1]['premise'].replace(HELPER, '$hook_short_reference_class_builtin_union_header')
    first, second = names.raw(b'First'), names.raw(b'Second')
    normalized = branches(b'Def333\\First', b'Def333\\Second')
    ast = union(first, second)
    for label, lexical in [
        ('consumer-shadow', names.context(namespace=b'Consumer333', imports=((b'First', b'stdClass'),))),
        ('missing-file', names.context(namespace=b'Def333', file=b'')),
        ('missing-line', names.context(namespace=b'Def333', line=0)),
    ]:
        check(label, ast, normalized, lexical, False)
    for position in (0, 1):
        for wrong in (b'', b'_', b'\\First', b'First\\', b'First\\\\Child', b'1First',
                      b'First\x00', b'First-Child', b'self', b'parent', b'static', b'int',
                      b'float', b'array', b'bool', b'string', b'null', b'true', b'false',
                      b'object', b'mixed', b'callable', b'iterable', b'void', b'never', b'Nested\\INT'):
            for kind in ('NName', 'NNameRelative', 'NNameFullyQualified'):
                raw = [first, second]; raw[position] = names.raw(wrong, kind)
                check('invalid-' + str(position) + '-' + kind + '-' + wrong.hex(), union(*raw), normalized, plain, False)
        for wrong in (b'boolean', b'integer', b'double', b'resource'):
            raw = [first, second]; raw[position] = names.raw(wrong)
            resolved = [b'Def333\\First', b'Def333\\Second']; resolved[position] = b'Def333\\' + wrong
            check('warning-' + str(position) + '-' + wrong.decode(), union(*raw), branches(*resolved), plain, False)
        raw = [first, second]; raw[position] = names.raw(b'First', 'NIdentifier')
        check('class-Identifier-' + str(position), union(*raw), normalized, plain, False)
        raw = [first, second]; raw[position] = names.raw(b'int', 'NIdentifier')
        check('builtin-arm-' + str(position), union(*raw), normalized, plain, False)
    for label, left, right, lexical, target in [
        ('identical', b'First', b'First', plain, b'Def333\\First'),
        ('case-duplicate', b'First', b'fIrSt', plain, b'Def333\\First'),
        ('two-aliases-same-target', b'Left', b'Right', names.context(namespace=b'Def333', imports=((b'Left', b'Payload333\\First'), (b'Right', b'Payload333\\First'))), b'Payload333\\First'),
    ]:
        check(label, union(names.raw(left), names.raw(right)), branches(target, target), lexical, False)
    check('case-duplicate-exact-raw-bits', union(first, names.raw(b'fIrSt')),
          branches(b'Def333\\First', b'Def333\\fIrSt'), plain, False)
    check('empty-union', union(), normalized, plain, False)
    check('single-union', union(first), branches(b'Def333\\First'), plain, False)
    check('three-classes', union(first, second, names.raw(b'Third')),
          branches(b'Def333\\First', b'Def333\\Second', b'Def333\\Third'), plain, False)
    check('two-classes-and-builtin', union(first, second, names.raw(b'array', 'NIdentifier')), normalized, plain, False)
    check('nullable-wrapper', names.raw(b'First', nullable=True), normalized, plain, False)
    check('intersection-wrapper', 'NIntersectionType (SEQUENCE ([' + first + ',' + second + '])) eps', normalized, plain, False)
    intersection = 'NIntersectionType (SEQUENCE ([' + first + ',' + second + '])) eps'
    check('DNF-member', union(intersection, names.raw(b'Third')), normalized, plain, False)
    for label, altered in [
        ('empty', 'eps'), ('missing', branches(b'Def333\\First')),
        ('extra', branches(b'Def333\\First', b'Def333\\Second', b'Def333\\Third')),
        ('intersection', '[(PTBRANCH ([PTCLASS ' + names.value(b'Def333\\First') + ',PTCLASS ' + names.value(b'Def333\\Second') + ']))]'),
        ('builtin', '[(PTBRANCH ([PTCLASS ' + names.value(b'Def333\\First') + '])),(PTBRANCH ([PTBUILTIN "object"]))]'),
    ]:
        check('normalized-' + label, ast, altered, plain, False)
    assert len({row['id'] for row in rows}) == len(rows)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(names.__file__), ROOT / 'tests/semantics/error_handler_run.py',
             ROOT / 'spec/semantics/modules.json', ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *modules]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'mode': 'fixture-SL',
              'source_agreement_credit': 0, 'native_observations': 0, 'passed': False}
    try:
        rows = assertions(); report['premises'] = len(rows)
        (out / 'assertions.json').write_text(json.dumps(rows, indent=2) + '\n')
        fixture = out / 'protocol.watsup'
        fixture.write_text('dec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + row['premise'] + '\n' for row in rows))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                      *map(str, modules), str(fixture)], out / 'check', 60)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after']
                            and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed'], report.get('stderr', '')[:2000]
    print('pass', report['premises'], 'independent nominal-pair assertions, source0')


if __name__ == '__main__':
    main()
