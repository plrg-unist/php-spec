#!/usr/bin/env python3
"""Independent exact class/array union order and lexical-context counterexamples."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import scoped_class_parentless_short_reference_get_hook_review_protocol as names
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
ARRAY = '(PTBRANCH ([PTBUILTIN "array"]))'


def union(*members):
    return 'NUnionType (SEQUENCE ([' + ','.join(members) + '])) eps'


def mask(name, array_first=False):
    cls = '(PTBRANCH ([PTCLASS ' + names.value(name) + ']))'
    return '[' + ','.join((ARRAY, cls) if array_first else (cls, ARRAY)) + ']'


def assertions():
    rows = []
    def check(label, ast, normalized, lexical, expected):
        rows.append({'id': label, 'expected': expected, 'premise': ('' if expected else '~') +
                     '$hook_short_reference_class_array_header(' + ast + ',' + normalized + ',' + lexical + ')'})
    plain = names.context(namespace=b'Def328')
    imported = names.context(namespace=b'Def328', imports=((b'Target328', b'Payload328\\Leaf'), (b'Prefix328', b'Payload328')))
    accepted = [
        ('global', b'stdClass', 'NName', b'stdClass', names.context(namespace=b'')),
        ('local', b'Leaf', 'NName', b'Def328\\Leaf', plain),
        ('qualified-local', b'Nested\\Leaf', 'NName', b'Def328\\Nested\\Leaf', plain),
        ('alias-case', b'tArGeT328', 'NName', b'Payload328\\Leaf', imported),
        ('prefix-case', b'pReFiX328\\lEaF', 'NName', b'Payload328\\lEaF', imported),
        ('relative', b'Leaf', 'NNameRelative', b'Def328\\Leaf', plain),
        ('relative-bypasses-alias', b'Target328', 'NNameRelative', b'Def328\\Target328', imported),
        ('fq-case', b'sTdClAsS', 'NNameFullyQualified', b'sTdClAsS', imported),
        ('fq-confusable-quiet', b'boolean', 'NNameFullyQualified', b'boolean', plain),
        ('relative-confusable-quiet', b'boolean', 'NNameRelative', b'Def328\\boolean', plain),
        ('high-byte', b'\x80Leaf', 'NName', b'Def328\\\x80Leaf', plain),
        ('underscore-component', b'Nested\\_', 'NName', b'Def328\\Nested\\_', plain),
    ]
    for label, raw_name, kind, resolved, lexical in accepted:
        cls = names.raw(raw_name, kind)
        for array_first in (False, True):
            suffix = '-array-class' if array_first else '-class-array'
            ast = union(names.raw(b'ArRaY', 'NIdentifier'), cls) if array_first else union(cls, names.raw(b'ARRAY', 'NIdentifier'))
            normalized = mask(resolved, array_first)
            check(label + suffix, ast, normalized, lexical, True)
            check(label + suffix + '-reversed-normalized', ast, mask(resolved, not array_first), lexical, False)
            check(label + suffix + '-different-class', ast, mask(resolved + b'X', array_first), lexical, False)
            check(label + suffix + '-different-case', ast, mask(resolved.swapcase(), array_first), lexical, False)
            for helper in ('$hook_short_reference_header(' + ast + ',' + normalized + ')',
                           '$hook_short_reference_scoped_header(' + ast + ',' + normalized + ',' + lexical + ')',
                           '$hook_short_reference_class_null_header(' + ast + ',' + normalized + ',' + lexical + ')',
                           '$hook_short_reference_class_false_header(' + ast + ',' + normalized + ',' + lexical + ')',
                           '$hook_short_reference_class_true_header(' + ast + ',' + normalized + ',' + lexical + ')',
                           '$hook_short_reference_class_bool_header(' + ast + ',' + normalized + ',' + lexical + ')',
                           '$hook_short_reference_class_int_header(' + ast + ',' + normalized + ',' + lexical + ')',
                           '$hook_short_reference_class_float_header(' + ast + ',' + normalized + ',' + lexical + ')',
                           '$hook_short_reference_class_string_header(' + ast + ',' + normalized + ',' + lexical + ')'):
                rows.append({'id': label + suffix + '-old-refusal-' + str(len(rows)), 'expected': False, 'premise': '~' + helper})
    cls = names.raw(b'Leaf'); array = names.raw(b'array', 'NIdentifier')
    ast = union(cls, array); normalized = mask(b'Def328\\Leaf')
    check('consumer-shadow-is-not-defining-context', ast, normalized,
          names.context(namespace=b'Consumer328', imports=((b'Leaf', b'stdClass'),)), False)
    check('missing-file', ast, normalized, names.context(namespace=b'Def328', file=b''), False)
    check('missing-line', ast, normalized, names.context(namespace=b'Def328', line=0), False)
    for kind in ('NName', 'NNameFullyQualified', 'NNameRelative'):
        check('array-is-not-Identifier-' + kind, union(cls, names.raw(b'array', kind)), normalized, plain, False)
        check('array-first-is-not-Identifier-' + kind, union(names.raw(b'array', kind), cls), mask(b'Def328\\Leaf', True), plain, False)
    for wrong in (b'', b'ARRAY\x00', b'true', b'null', b'bool', b'false', b'array\\Leaf'):
        check('wrong-array-' + wrong.hex(), union(cls, names.raw(wrong, 'NIdentifier')), normalized, plain, False)
    check('wrong-array-int', union(cls, names.raw(b'int', 'NIdentifier')), normalized, plain, False)
    check('wrong-array-float', union(cls, names.raw(b'float', 'NIdentifier')), normalized, plain, False)
    check('wrong-array-string', union(cls, names.raw(b'string', 'NIdentifier')), normalized, plain, False)
    for raw_name in (b'', b'_', b'\\Leaf', b'Leaf\\', b'Leaf\\\\Child', b'1Leaf', b'Leaf\x00', b'Leaf-Child',
                     b'self', b'PaReNt', b'STATIC', b'array', b'callable', b'int', b'float', b'string', b'bool',
                     b'object', b'mixed', b'null', b'true', b'false', b'void', b'never', b'iterable', b'Nested\\INT'):
        for kind in ('NName', 'NNameFullyQualified', 'NNameRelative'):
            resolved = raw_name if kind == 'NNameFullyQualified' else b'Def328\\' + raw_name
            check('invalid-class-' + kind + '-' + raw_name.hex(), union(names.raw(raw_name, kind), array), mask(resolved), plain, False)
    for kind in ('NName', 'NNameRelative'):
        check('self-must-not-use-known-scope-' + kind, union(names.raw(b'SeLf', kind), array), mask(b'Def328\\Box323'), plain, False)
    for raw_name in (b'boolean', b'integer', b'double', b'resource'):
        check('plain-confusable-warning-' + raw_name.decode(), union(names.raw(raw_name), array), mask(b'Def328\\' + raw_name), plain, False)
    check('imported-global-underscore-warning', union(names.raw(b'Target328'), array), mask(b'_'),
          names.context(namespace=b'Def328', imports=((b'Target328', b'_'),)), False)
    for label, edited in (
        ('single', cls), ('nullable', 'NNullableType (' + cls + ') eps'),
        ('empty', union()), ('singleton', union(cls)), ('duplicate-array', union(cls, array, array)),
        ('extra-builtin', union(cls, array, names.raw(b'int', 'NIdentifier'))),
        ('extra-class', union(cls, array, names.raw(b'Other'))),
        ('class-Identifier', union(names.raw(b'Leaf', 'NIdentifier'), array)),
        ('intersection', union('NIntersectionType (SEQUENCE ([' + cls + ',' + names.raw(b'Other') + '])) eps', array)),
    ):
        check('raw-shape-' + label, edited, normalized, plain, False)
    for label, edited in (
        ('empty', 'eps'), ('class-only', names.mask(b'Def328\\Leaf')),
        ('array-only', '[' + ARRAY + ']'),
        ('broadened-bool', normalized.replace('PTBUILTIN "array"', 'PTBUILTIN "bool"')),
        ('wrong-true', normalized.replace('PTBUILTIN "array"', 'PTBUILTIN "true"')),
        ('wrong-null', normalized.replace('PTBUILTIN "array"', 'PTBUILTIN "null"')),
        ('wrong-false', normalized.replace('PTBUILTIN "array"', 'PTBUILTIN "false"')),
        ('extra-array', normalized[:-1] + ',' + ARRAY + ']'),
        ('builtin', '[(PTBRANCH ([PTBUILTIN "object"])),' + ARRAY + ']'),
        ('scope', '[(PTBRANCH ([PTSELF])),' + ARRAY + ']'),
        ('intersection', '[(PTBRANCH ([PTCLASS ([65]),PTCLASS ([66])])),' + ARRAY + ']'),
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
    print('pass', report['premises'], 'independent class/array assertions, source0')


if __name__ == '__main__':
    main()
