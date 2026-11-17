#!/usr/bin/env python3
"""Independent exact class/null union order and lexical-context counterexamples."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import scoped_class_parentless_short_reference_get_hook_review_protocol as names
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
NULL = '(PTBRANCH ([PTBUILTIN "null"]))'


def union(*members):
    return 'NUnionType (SEQUENCE ([' + ','.join(members) + '])) eps'


def mask(name, null_first=False):
    cls = '(PTBRANCH ([PTCLASS ' + names.value(name) + ']))'
    return '[' + ','.join((NULL, cls) if null_first else (cls, NULL)) + ']'


def assertions():
    rows = []
    def check(label, ast, normalized, lexical, expected):
        rows.append({'id': label, 'expected': expected, 'premise': ('' if expected else '~') +
                     '$hook_short_reference_class_null_header(' + ast + ',' + normalized + ',' + lexical + ')'})
    plain = names.context(namespace=b'Def324')
    imported = names.context(namespace=b'Def324', imports=((b'Target324', b'Payload324\\Leaf'), (b'Prefix324', b'Payload324')))
    accepted = [
        ('global', b'stdClass', 'NName', b'stdClass', names.context(namespace=b'')),
        ('local', b'Leaf', 'NName', b'Def324\\Leaf', plain),
        ('qualified-local', b'Nested\\Leaf', 'NName', b'Def324\\Nested\\Leaf', plain),
        ('alias-case', b'tArGeT324', 'NName', b'Payload324\\Leaf', imported),
        ('prefix-case', b'pReFiX324\\lEaF', 'NName', b'Payload324\\lEaF', imported),
        ('relative', b'Leaf', 'NNameRelative', b'Def324\\Leaf', plain),
        ('relative-bypasses-alias', b'Target324', 'NNameRelative', b'Def324\\Target324', imported),
        ('fq-case', b'sTdClAsS', 'NNameFullyQualified', b'sTdClAsS', imported),
        ('fq-confusable-quiet', b'boolean', 'NNameFullyQualified', b'boolean', plain),
        ('relative-confusable-quiet', b'boolean', 'NNameRelative', b'Def324\\boolean', plain),
        ('high-byte', b'\x80Leaf', 'NName', b'Def324\\\x80Leaf', plain),
        ('underscore-component', b'Nested\\_', 'NName', b'Def324\\Nested\\_', plain),
    ]
    for label, raw_name, kind, resolved, lexical in accepted:
        cls = names.raw(raw_name, kind)
        for null_first in (False, True):
            suffix = '-null-class' if null_first else '-class-null'
            ast = union(names.raw(b'NuLl', 'NIdentifier'), cls) if null_first else union(cls, names.raw(b'NULL', 'NIdentifier'))
            normalized = mask(resolved, null_first)
            check(label + suffix, ast, normalized, lexical, True)
            check(label + suffix + '-reversed-normalized', ast, mask(resolved, not null_first), lexical, False)
            check(label + suffix + '-different-class', ast, mask(resolved + b'X', null_first), lexical, False)
            check(label + suffix + '-different-case', ast, mask(resolved.swapcase(), null_first), lexical, False)
            for helper in ('$hook_short_reference_header(' + ast + ',' + normalized + ')',
                           '$hook_short_reference_scoped_header(' + ast + ',' + normalized + ',' + lexical + ')'):
                rows.append({'id': label + suffix + '-old-refusal-' + str(len(rows)), 'expected': False, 'premise': '~' + helper})
    cls = names.raw(b'Leaf'); null = names.raw(b'null', 'NIdentifier')
    ast = union(cls, null); normalized = mask(b'Def324\\Leaf')
    check('consumer-shadow-is-not-defining-context', ast, normalized,
          names.context(namespace=b'Consumer324', imports=((b'Leaf', b'stdClass'),)), False)
    check('missing-file', ast, normalized, names.context(namespace=b'Def324', file=b''), False)
    check('missing-line', ast, normalized, names.context(namespace=b'Def324', line=0), False)
    for kind in ('NName', 'NNameFullyQualified', 'NNameRelative'):
        check('null-is-not-Identifier-' + kind, union(cls, names.raw(b'null', kind)), normalized, plain, False)
        check('null-first-is-not-Identifier-' + kind, union(names.raw(b'null', kind), cls), mask(b'Def324\\Leaf', True), plain, False)
    for wrong in (b'', b'NULL\x00', b'false', b'int', b'null\\Leaf'):
        check('wrong-null-' + wrong.hex(), union(cls, names.raw(wrong, 'NIdentifier')), normalized, plain, False)
    for raw_name in (b'', b'_', b'\\Leaf', b'Leaf\\', b'Leaf\\\\Child', b'1Leaf', b'Leaf\x00', b'Leaf-Child',
                     b'self', b'PaReNt', b'STATIC', b'array', b'callable', b'int', b'float', b'string', b'bool',
                     b'object', b'mixed', b'null', b'true', b'false', b'void', b'never', b'iterable', b'Nested\\INT'):
        for kind in ('NName', 'NNameFullyQualified', 'NNameRelative'):
            resolved = raw_name if kind == 'NNameFullyQualified' else b'Def324\\' + raw_name
            check('invalid-class-' + kind + '-' + raw_name.hex(), union(names.raw(raw_name, kind), null), mask(resolved), plain, False)
    for kind in ('NName', 'NNameRelative'):
        check('self-must-not-use-known-scope-' + kind, union(names.raw(b'SeLf', kind), null), mask(b'Def324\\Box323'), plain, False)
    for raw_name in (b'boolean', b'integer', b'double', b'resource'):
        check('plain-confusable-warning-' + raw_name.decode(), union(names.raw(raw_name), null), mask(b'Def324\\' + raw_name), plain, False)
    check('imported-global-underscore-warning', union(names.raw(b'Target324'), null), mask(b'_'),
          names.context(namespace=b'Def324', imports=((b'Target324', b'_'),)), False)
    for label, edited in (
        ('single', cls), ('nullable', 'NNullableType (' + cls + ') eps'),
        ('empty', union()), ('singleton', union(cls)), ('duplicate-null', union(cls, null, null)),
        ('extra-builtin', union(cls, null, names.raw(b'int', 'NIdentifier'))),
        ('extra-class', union(cls, null, names.raw(b'Other'))),
        ('class-Identifier', union(names.raw(b'Leaf', 'NIdentifier'), null)),
        ('intersection', union('NIntersectionType (SEQUENCE ([' + cls + ',' + names.raw(b'Other') + '])) eps', null)),
    ):
        check('raw-shape-' + label, edited, normalized, plain, False)
    for label, edited in (
        ('empty', 'eps'), ('class-only', names.mask(b'Def324\\Leaf')),
        ('null-only', '[' + NULL + ']'), ('extra-null', normalized[:-1] + ',' + NULL + ']'),
        ('builtin', '[(PTBRANCH ([PTBUILTIN "object"])),' + NULL + ']'),
        ('scope', '[(PTBRANCH ([PTSELF])),' + NULL + ']'),
        ('intersection', '[(PTBRANCH ([PTCLASS ([65]),PTCLASS ([66])])),' + NULL + ']'),
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
    print('pass', report['premises'], 'independent class/null assertions, source0')


if __name__ == '__main__':
    main()
