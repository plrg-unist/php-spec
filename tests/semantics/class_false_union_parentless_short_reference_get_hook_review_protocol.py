#!/usr/bin/env python3
"""Independent exact class/false union order and lexical-context counterexamples."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import scoped_class_parentless_short_reference_get_hook_review_protocol as names
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
FALSE = '(PTBRANCH ([PTBUILTIN "false"]))'


def union(*members):
    return 'NUnionType (SEQUENCE ([' + ','.join(members) + '])) eps'


def mask(name, false_first=False):
    cls = '(PTBRANCH ([PTCLASS ' + names.value(name) + ']))'
    return '[' + ','.join((FALSE, cls) if false_first else (cls, FALSE)) + ']'


def assertions():
    rows = []
    def check(label, ast, normalized, lexical, expected):
        rows.append({'id': label, 'expected': expected, 'premise': ('' if expected else '~') +
                     '$hook_short_reference_class_false_header(' + ast + ',' + normalized + ',' + lexical + ')'})
    plain = names.context(namespace=b'Def325')
    imported = names.context(namespace=b'Def325', imports=((b'Target325', b'Payload325\\Leaf'), (b'Prefix325', b'Payload325')))
    accepted = [
        ('global', b'stdClass', 'NName', b'stdClass', names.context(namespace=b'')),
        ('local', b'Leaf', 'NName', b'Def325\\Leaf', plain),
        ('qualified-local', b'Nested\\Leaf', 'NName', b'Def325\\Nested\\Leaf', plain),
        ('alias-case', b'tArGeT325', 'NName', b'Payload325\\Leaf', imported),
        ('prefix-case', b'pReFiX325\\lEaF', 'NName', b'Payload325\\lEaF', imported),
        ('relative', b'Leaf', 'NNameRelative', b'Def325\\Leaf', plain),
        ('relative-bypasses-alias', b'Target325', 'NNameRelative', b'Def325\\Target325', imported),
        ('fq-case', b'sTdClAsS', 'NNameFullyQualified', b'sTdClAsS', imported),
        ('fq-confusable-quiet', b'boolean', 'NNameFullyQualified', b'boolean', plain),
        ('relative-confusable-quiet', b'boolean', 'NNameRelative', b'Def325\\boolean', plain),
        ('high-byte', b'\x80Leaf', 'NName', b'Def325\\\x80Leaf', plain),
        ('underscore-component', b'Nested\\_', 'NName', b'Def325\\Nested\\_', plain),
    ]
    for label, raw_name, kind, resolved, lexical in accepted:
        cls = names.raw(raw_name, kind)
        for false_first in (False, True):
            suffix = '-false-class' if false_first else '-class-false'
            ast = union(names.raw(b'FaLsE', 'NIdentifier'), cls) if false_first else union(cls, names.raw(b'FALSE', 'NIdentifier'))
            normalized = mask(resolved, false_first)
            check(label + suffix, ast, normalized, lexical, True)
            check(label + suffix + '-reversed-normalized', ast, mask(resolved, not false_first), lexical, False)
            check(label + suffix + '-different-class', ast, mask(resolved + b'X', false_first), lexical, False)
            check(label + suffix + '-different-case', ast, mask(resolved.swapcase(), false_first), lexical, False)
            for helper in ('$hook_short_reference_header(' + ast + ',' + normalized + ')',
                           '$hook_short_reference_scoped_header(' + ast + ',' + normalized + ',' + lexical + ')',
                           '$hook_short_reference_class_null_header(' + ast + ',' + normalized + ',' + lexical + ')'):
                rows.append({'id': label + suffix + '-old-refusal-' + str(len(rows)), 'expected': False, 'premise': '~' + helper})
    cls = names.raw(b'Leaf'); false = names.raw(b'false', 'NIdentifier')
    ast = union(cls, false); normalized = mask(b'Def325\\Leaf')
    check('consumer-shadow-is-not-defining-context', ast, normalized,
          names.context(namespace=b'Consumer325', imports=((b'Leaf', b'stdClass'),)), False)
    check('missing-file', ast, normalized, names.context(namespace=b'Def325', file=b''), False)
    check('missing-line', ast, normalized, names.context(namespace=b'Def325', line=0), False)
    for kind in ('NName', 'NNameFullyQualified', 'NNameRelative'):
        check('false-is-not-Identifier-' + kind, union(cls, names.raw(b'false', kind)), normalized, plain, False)
        check('false-first-is-not-Identifier-' + kind, union(names.raw(b'false', kind), cls), mask(b'Def325\\Leaf', True), plain, False)
    for wrong in (b'', b'FALSE\x00', b'true', b'null', b'bool', b'int', b'false\\Leaf'):
        check('wrong-false-' + wrong.hex(), union(cls, names.raw(wrong, 'NIdentifier')), normalized, plain, False)
    for raw_name in (b'', b'_', b'\\Leaf', b'Leaf\\', b'Leaf\\\\Child', b'1Leaf', b'Leaf\x00', b'Leaf-Child',
                     b'self', b'PaReNt', b'STATIC', b'array', b'callable', b'int', b'float', b'string', b'bool',
                     b'object', b'mixed', b'null', b'true', b'false', b'void', b'never', b'iterable', b'Nested\\INT'):
        for kind in ('NName', 'NNameFullyQualified', 'NNameRelative'):
            resolved = raw_name if kind == 'NNameFullyQualified' else b'Def325\\' + raw_name
            check('invalid-class-' + kind + '-' + raw_name.hex(), union(names.raw(raw_name, kind), false), mask(resolved), plain, False)
    for kind in ('NName', 'NNameRelative'):
        check('self-must-not-use-known-scope-' + kind, union(names.raw(b'SeLf', kind), false), mask(b'Def325\\Box323'), plain, False)
    for raw_name in (b'boolean', b'integer', b'double', b'resource'):
        check('plain-confusable-warning-' + raw_name.decode(), union(names.raw(raw_name), false), mask(b'Def325\\' + raw_name), plain, False)
    check('imported-global-underscore-warning', union(names.raw(b'Target325'), false), mask(b'_'),
          names.context(namespace=b'Def325', imports=((b'Target325', b'_'),)), False)
    for label, edited in (
        ('single', cls), ('nullable', 'NNullableType (' + cls + ') eps'),
        ('empty', union()), ('singleton', union(cls)), ('duplicate-false', union(cls, false, false)),
        ('extra-builtin', union(cls, false, names.raw(b'int', 'NIdentifier'))),
        ('extra-class', union(cls, false, names.raw(b'Other'))),
        ('class-Identifier', union(names.raw(b'Leaf', 'NIdentifier'), false)),
        ('intersection', union('NIntersectionType (SEQUENCE ([' + cls + ',' + names.raw(b'Other') + '])) eps', false)),
    ):
        check('raw-shape-' + label, edited, normalized, plain, False)
    for label, edited in (
        ('empty', 'eps'), ('class-only', names.mask(b'Def325\\Leaf')),
        ('false-only', '[' + FALSE + ']'),
        ('broadened-bool', normalized.replace('PTBUILTIN "false"', 'PTBUILTIN "bool"')),
        ('wrong-true', normalized.replace('PTBUILTIN "false"', 'PTBUILTIN "true"')),
        ('wrong-null', normalized.replace('PTBUILTIN "false"', 'PTBUILTIN "null"')),
        ('extra-false', normalized[:-1] + ',' + FALSE + ']'),
        ('builtin', '[(PTBRANCH ([PTBUILTIN "object"])),' + FALSE + ']'),
        ('scope', '[(PTBRANCH ([PTSELF])),' + FALSE + ']'),
        ('intersection', '[(PTBRANCH ([PTCLASS ([65]),PTCLASS ([66])])),' + FALSE + ']'),
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
    print('pass', report['premises'], 'independent class/false assertions, source0')


if __name__ == '__main__':
    main()
