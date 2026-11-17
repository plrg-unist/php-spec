#!/usr/bin/env python3
"""Independent exact class/bool union order and lexical-context counterexamples."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import scoped_class_parentless_short_reference_get_hook_review_protocol as names
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
BOOL = '(PTBRANCH ([PTBUILTIN "bool"]))'


def union(*members):
    return 'NUnionType (SEQUENCE ([' + ','.join(members) + '])) eps'


def mask(name, bool_first=False):
    cls = '(PTBRANCH ([PTCLASS ' + names.value(name) + ']))'
    return '[' + ','.join((BOOL, cls) if bool_first else (cls, BOOL)) + ']'


def assertions():
    rows = []
    def check(label, ast, normalized, lexical, expected):
        rows.append({'id': label, 'expected': expected, 'premise': ('' if expected else '~') +
                     '$hook_short_reference_class_bool_header(' + ast + ',' + normalized + ',' + lexical + ')'})
    plain = names.context(namespace=b'Def327')
    imported = names.context(namespace=b'Def327', imports=((b'Target327', b'Payload327\\Leaf'), (b'Prefix327', b'Payload327')))
    accepted = [
        ('global', b'stdClass', 'NName', b'stdClass', names.context(namespace=b'')),
        ('local', b'Leaf', 'NName', b'Def327\\Leaf', plain),
        ('qualified-local', b'Nested\\Leaf', 'NName', b'Def327\\Nested\\Leaf', plain),
        ('alias-case', b'tArGeT327', 'NName', b'Payload327\\Leaf', imported),
        ('prefix-case', b'pReFiX327\\lEaF', 'NName', b'Payload327\\lEaF', imported),
        ('relative', b'Leaf', 'NNameRelative', b'Def327\\Leaf', plain),
        ('relative-bypasses-alias', b'Target327', 'NNameRelative', b'Def327\\Target327', imported),
        ('fq-case', b'sTdClAsS', 'NNameFullyQualified', b'sTdClAsS', imported),
        ('fq-confusable-quiet', b'boolean', 'NNameFullyQualified', b'boolean', plain),
        ('relative-confusable-quiet', b'boolean', 'NNameRelative', b'Def327\\boolean', plain),
        ('high-byte', b'\x80Leaf', 'NName', b'Def327\\\x80Leaf', plain),
        ('underscore-component', b'Nested\\_', 'NName', b'Def327\\Nested\\_', plain),
    ]
    for label, raw_name, kind, resolved, lexical in accepted:
        cls = names.raw(raw_name, kind)
        for bool_first in (False, True):
            suffix = '-bool-class' if bool_first else '-class-bool'
            ast = union(names.raw(b'BoOl', 'NIdentifier'), cls) if bool_first else union(cls, names.raw(b'BOOL', 'NIdentifier'))
            normalized = mask(resolved, bool_first)
            check(label + suffix, ast, normalized, lexical, True)
            check(label + suffix + '-reversed-normalized', ast, mask(resolved, not bool_first), lexical, False)
            check(label + suffix + '-different-class', ast, mask(resolved + b'X', bool_first), lexical, False)
            check(label + suffix + '-different-case', ast, mask(resolved.swapcase(), bool_first), lexical, False)
            for helper in ('$hook_short_reference_header(' + ast + ',' + normalized + ')',
                           '$hook_short_reference_scoped_header(' + ast + ',' + normalized + ',' + lexical + ')',
                           '$hook_short_reference_class_null_header(' + ast + ',' + normalized + ',' + lexical + ')',
                           '$hook_short_reference_class_false_header(' + ast + ',' + normalized + ',' + lexical + ')',
                           '$hook_short_reference_class_true_header(' + ast + ',' + normalized + ',' + lexical + ')'):
                rows.append({'id': label + suffix + '-old-refusal-' + str(len(rows)), 'expected': False, 'premise': '~' + helper})
    cls = names.raw(b'Leaf'); bool = names.raw(b'bool', 'NIdentifier')
    ast = union(cls, bool); normalized = mask(b'Def327\\Leaf')
    check('consumer-shadow-is-not-defining-context', ast, normalized,
          names.context(namespace=b'Consumer327', imports=((b'Leaf', b'stdClass'),)), False)
    check('missing-file', ast, normalized, names.context(namespace=b'Def327', file=b''), False)
    check('missing-line', ast, normalized, names.context(namespace=b'Def327', line=0), False)
    for kind in ('NName', 'NNameFullyQualified', 'NNameRelative'):
        check('bool-is-not-Identifier-' + kind, union(cls, names.raw(b'bool', kind)), normalized, plain, False)
        check('bool-first-is-not-Identifier-' + kind, union(names.raw(b'bool', kind), cls), mask(b'Def327\\Leaf', True), plain, False)
    for wrong in (b'', b'BOOL\x00', b'false', b'null', b'true', b'int', b'bool\\Leaf'):
        check('wrong-bool-' + wrong.hex(), union(cls, names.raw(wrong, 'NIdentifier')), normalized, plain, False)
    for raw_name in (b'', b'_', b'\\Leaf', b'Leaf\\', b'Leaf\\\\Child', b'1Leaf', b'Leaf\x00', b'Leaf-Child',
                     b'self', b'PaReNt', b'STATIC', b'array', b'callable', b'int', b'float', b'string', b'bool',
                     b'object', b'mixed', b'null', b'true', b'false', b'void', b'never', b'iterable', b'Nested\\INT'):
        for kind in ('NName', 'NNameFullyQualified', 'NNameRelative'):
            resolved = raw_name if kind == 'NNameFullyQualified' else b'Def327\\' + raw_name
            check('invalid-class-' + kind + '-' + raw_name.hex(), union(names.raw(raw_name, kind), bool), mask(resolved), plain, False)
    for kind in ('NName', 'NNameRelative'):
        check('self-must-not-use-known-scope-' + kind, union(names.raw(b'SeLf', kind), bool), mask(b'Def327\\Box323'), plain, False)
    for raw_name in (b'boolean', b'integer', b'double', b'resource'):
        check('plain-confusable-warning-' + raw_name.decode(), union(names.raw(raw_name), bool), mask(b'Def327\\' + raw_name), plain, False)
    check('imported-global-underscore-warning', union(names.raw(b'Target327'), bool), mask(b'_'),
          names.context(namespace=b'Def327', imports=((b'Target327', b'_'),)), False)
    for label, edited in (
        ('single', cls), ('nullable', 'NNullableType (' + cls + ') eps'),
        ('empty', union()), ('singleton', union(cls)), ('duplicate-bool', union(cls, bool, bool)),
        ('extra-builtin', union(cls, bool, names.raw(b'int', 'NIdentifier'))),
        ('extra-class', union(cls, bool, names.raw(b'Other'))),
        ('class-Identifier', union(names.raw(b'Leaf', 'NIdentifier'), bool)),
        ('intersection', union('NIntersectionType (SEQUENCE ([' + cls + ',' + names.raw(b'Other') + '])) eps', bool)),
    ):
        check('raw-shape-' + label, edited, normalized, plain, False)
    for label, edited in (
        ('empty', 'eps'), ('class-only', names.mask(b'Def327\\Leaf')),
        ('bool-only', '[' + BOOL + ']'),
        ('true-only', normalized.replace('PTBUILTIN "bool"', 'PTBUILTIN "true"')),
        ('wrong-false', normalized.replace('PTBUILTIN "bool"', 'PTBUILTIN "false"')),
        ('wrong-null', normalized.replace('PTBUILTIN "bool"', 'PTBUILTIN "null"')),
        ('extra-bool', normalized[:-1] + ',' + BOOL + ']'),
        ('builtin', '[(PTBRANCH ([PTBUILTIN "object"])),' + BOOL + ']'),
        ('scope', '[(PTBRANCH ([PTSELF])),' + BOOL + ']'),
        ('intersection', '[(PTBRANCH ([PTCLASS ([65]),PTCLASS ([66])])),' + BOOL + ']'),
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
    print('pass', report['premises'], 'independent class/bool assertions, source0')


if __name__ == '__main__':
    main()
