#!/usr/bin/env python3
"""Independent exact class/true union order and lexical-context counterexamples."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import scoped_class_parentless_short_reference_get_hook_review_protocol as names
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
TRUE = '(PTBRANCH ([PTBUILTIN "true"]))'


def union(*members):
    return 'NUnionType (SEQUENCE ([' + ','.join(members) + '])) eps'


def mask(name, true_first=False):
    cls = '(PTBRANCH ([PTCLASS ' + names.value(name) + ']))'
    return '[' + ','.join((TRUE, cls) if true_first else (cls, TRUE)) + ']'


def assertions():
    rows = []
    def check(label, ast, normalized, lexical, expected):
        rows.append({'id': label, 'expected': expected, 'premise': ('' if expected else '~') +
                     '$hook_short_reference_class_true_header(' + ast + ',' + normalized + ',' + lexical + ')'})
    plain = names.context(namespace=b'Def326')
    imported = names.context(namespace=b'Def326', imports=((b'Target326', b'Payload326\\Leaf'), (b'Prefix326', b'Payload326')))
    accepted = [
        ('global', b'stdClass', 'NName', b'stdClass', names.context(namespace=b'')),
        ('local', b'Leaf', 'NName', b'Def326\\Leaf', plain),
        ('qualified-local', b'Nested\\Leaf', 'NName', b'Def326\\Nested\\Leaf', plain),
        ('alias-case', b'tArGeT326', 'NName', b'Payload326\\Leaf', imported),
        ('prefix-case', b'pReFiX326\\lEaF', 'NName', b'Payload326\\lEaF', imported),
        ('relative', b'Leaf', 'NNameRelative', b'Def326\\Leaf', plain),
        ('relative-bypasses-alias', b'Target326', 'NNameRelative', b'Def326\\Target326', imported),
        ('fq-case', b'sTdClAsS', 'NNameFullyQualified', b'sTdClAsS', imported),
        ('fq-confusable-quiet', b'boolean', 'NNameFullyQualified', b'boolean', plain),
        ('relative-confusable-quiet', b'boolean', 'NNameRelative', b'Def326\\boolean', plain),
        ('high-byte', b'\x80Leaf', 'NName', b'Def326\\\x80Leaf', plain),
        ('underscore-component', b'Nested\\_', 'NName', b'Def326\\Nested\\_', plain),
    ]
    for label, raw_name, kind, resolved, lexical in accepted:
        cls = names.raw(raw_name, kind)
        for true_first in (False, True):
            suffix = '-true-class' if true_first else '-class-true'
            ast = union(names.raw(b'TrUe', 'NIdentifier'), cls) if true_first else union(cls, names.raw(b'TRUE', 'NIdentifier'))
            normalized = mask(resolved, true_first)
            check(label + suffix, ast, normalized, lexical, True)
            check(label + suffix + '-reversed-normalized', ast, mask(resolved, not true_first), lexical, False)
            check(label + suffix + '-different-class', ast, mask(resolved + b'X', true_first), lexical, False)
            check(label + suffix + '-different-case', ast, mask(resolved.swapcase(), true_first), lexical, False)
            for helper in ('$hook_short_reference_header(' + ast + ',' + normalized + ')',
                           '$hook_short_reference_scoped_header(' + ast + ',' + normalized + ',' + lexical + ')',
                           '$hook_short_reference_class_null_header(' + ast + ',' + normalized + ',' + lexical + ')',
                           '$hook_short_reference_class_false_header(' + ast + ',' + normalized + ',' + lexical + ')'):
                rows.append({'id': label + suffix + '-old-refusal-' + str(len(rows)), 'expected': False, 'premise': '~' + helper})
    cls = names.raw(b'Leaf'); true = names.raw(b'true', 'NIdentifier')
    ast = union(cls, true); normalized = mask(b'Def326\\Leaf')
    check('consumer-shadow-is-not-defining-context', ast, normalized,
          names.context(namespace=b'Consumer326', imports=((b'Leaf', b'stdClass'),)), False)
    check('missing-file', ast, normalized, names.context(namespace=b'Def326', file=b''), False)
    check('missing-line', ast, normalized, names.context(namespace=b'Def326', line=0), False)
    for kind in ('NName', 'NNameFullyQualified', 'NNameRelative'):
        check('true-is-not-Identifier-' + kind, union(cls, names.raw(b'true', kind)), normalized, plain, False)
        check('true-first-is-not-Identifier-' + kind, union(names.raw(b'true', kind), cls), mask(b'Def326\\Leaf', True), plain, False)
    for wrong in (b'', b'TRUE\x00', b'false', b'null', b'bool', b'int', b'true\\Leaf'):
        check('wrong-true-' + wrong.hex(), union(cls, names.raw(wrong, 'NIdentifier')), normalized, plain, False)
    for raw_name in (b'', b'_', b'\\Leaf', b'Leaf\\', b'Leaf\\\\Child', b'1Leaf', b'Leaf\x00', b'Leaf-Child',
                     b'self', b'PaReNt', b'STATIC', b'array', b'callable', b'int', b'float', b'string', b'bool',
                     b'object', b'mixed', b'null', b'true', b'false', b'void', b'never', b'iterable', b'Nested\\INT'):
        for kind in ('NName', 'NNameFullyQualified', 'NNameRelative'):
            resolved = raw_name if kind == 'NNameFullyQualified' else b'Def326\\' + raw_name
            check('invalid-class-' + kind + '-' + raw_name.hex(), union(names.raw(raw_name, kind), true), mask(resolved), plain, False)
    for kind in ('NName', 'NNameRelative'):
        check('self-must-not-use-known-scope-' + kind, union(names.raw(b'SeLf', kind), true), mask(b'Def326\\Box323'), plain, False)
    for raw_name in (b'boolean', b'integer', b'double', b'resource'):
        check('plain-confusable-warning-' + raw_name.decode(), union(names.raw(raw_name), true), mask(b'Def326\\' + raw_name), plain, False)
    check('imported-global-underscore-warning', union(names.raw(b'Target326'), true), mask(b'_'),
          names.context(namespace=b'Def326', imports=((b'Target326', b'_'),)), False)
    for label, edited in (
        ('single', cls), ('nullable', 'NNullableType (' + cls + ') eps'),
        ('empty', union()), ('singleton', union(cls)), ('duplicate-true', union(cls, true, true)),
        ('extra-builtin', union(cls, true, names.raw(b'int', 'NIdentifier'))),
        ('extra-class', union(cls, true, names.raw(b'Other'))),
        ('class-Identifier', union(names.raw(b'Leaf', 'NIdentifier'), true)),
        ('intersection', union('NIntersectionType (SEQUENCE ([' + cls + ',' + names.raw(b'Other') + '])) eps', true)),
    ):
        check('raw-shape-' + label, edited, normalized, plain, False)
    for label, edited in (
        ('empty', 'eps'), ('class-only', names.mask(b'Def326\\Leaf')),
        ('true-only', '[' + TRUE + ']'),
        ('broadened-bool', normalized.replace('PTBUILTIN "true"', 'PTBUILTIN "bool"')),
        ('wrong-false', normalized.replace('PTBUILTIN "true"', 'PTBUILTIN "false"')),
        ('wrong-null', normalized.replace('PTBUILTIN "true"', 'PTBUILTIN "null"')),
        ('extra-true', normalized[:-1] + ',' + TRUE + ']'),
        ('builtin', '[(PTBRANCH ([PTBUILTIN "object"])),' + TRUE + ']'),
        ('scope', '[(PTBRANCH ([PTSELF])),' + TRUE + ']'),
        ('intersection', '[(PTBRANCH ([PTCLASS ([65]),PTCLASS ([66])])),' + TRUE + ']'),
    ):
        check('normalized-shape-' + label, ast, edited, plain, False)
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
    print('pass', report['premises'], 'independent class/true assertions, source0')


if __name__ == '__main__':
    main()
