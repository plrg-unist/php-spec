#!/usr/bin/env python3
"""Independent exact class/string union order and lexical-context counterexamples."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import scoped_class_parentless_short_reference_get_hook_review_protocol as names
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
STRING = '(PTBRANCH ([PTBUILTIN "string"]))'


def union(*members):
    return 'NUnionType (SEQUENCE ([' + ','.join(members) + '])) eps'


def mask(name, string_first=False):
    cls = '(PTBRANCH ([PTCLASS ' + names.value(name) + ']))'
    return '[' + ','.join((STRING, cls) if string_first else (cls, STRING)) + ']'


def assertions():
    rows = []
    def check(label, ast, normalized, lexical, expected):
        rows.append({'id': label, 'expected': expected, 'premise': ('' if expected else '~') +
                     '$hook_short_reference_class_string_header(' + ast + ',' + normalized + ',' + lexical + ')'})
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
        for string_first in (False, True):
            suffix = '-string-class' if string_first else '-class-string'
            ast = union(names.raw(b'StRiNg', 'NIdentifier'), cls) if string_first else union(cls, names.raw(b'STRING', 'NIdentifier'))
            normalized = mask(resolved, string_first)
            check(label + suffix, ast, normalized, lexical, True)
            check(label + suffix + '-reversed-normalized', ast, mask(resolved, not string_first), lexical, False)
            check(label + suffix + '-different-class', ast, mask(resolved + b'X', string_first), lexical, False)
            check(label + suffix + '-different-case', ast, mask(resolved.swapcase(), string_first), lexical, False)
            for helper in ('$hook_short_reference_header(' + ast + ',' + normalized + ')',
                           '$hook_short_reference_scoped_header(' + ast + ',' + normalized + ',' + lexical + ')',
                           '$hook_short_reference_class_null_header(' + ast + ',' + normalized + ',' + lexical + ')',
                           '$hook_short_reference_class_false_header(' + ast + ',' + normalized + ',' + lexical + ')',
                           '$hook_short_reference_class_true_header(' + ast + ',' + normalized + ',' + lexical + ')',
                           '$hook_short_reference_class_bool_header(' + ast + ',' + normalized + ',' + lexical + ')',
                           '$hook_short_reference_class_int_header(' + ast + ',' + normalized + ',' + lexical + ')',
                           '$hook_short_reference_class_float_header(' + ast + ',' + normalized + ',' + lexical + ')'):
                rows.append({'id': label + suffix + '-old-refusal-' + str(len(rows)), 'expected': False, 'premise': '~' + helper})
    cls = names.raw(b'Leaf'); string = names.raw(b'string', 'NIdentifier')
    ast = union(cls, string); normalized = mask(b'Def328\\Leaf')
    check('consumer-shadow-is-not-defining-context', ast, normalized,
          names.context(namespace=b'Consumer328', imports=((b'Leaf', b'stdClass'),)), False)
    check('missing-file', ast, normalized, names.context(namespace=b'Def328', file=b''), False)
    check('missing-line', ast, normalized, names.context(namespace=b'Def328', line=0), False)
    for kind in ('NName', 'NNameFullyQualified', 'NNameRelative'):
        check('string-is-not-Identifier-' + kind, union(cls, names.raw(b'string', kind)), normalized, plain, False)
        check('string-first-is-not-Identifier-' + kind, union(names.raw(b'string', kind), cls), mask(b'Def328\\Leaf', True), plain, False)
    for wrong in (b'', b'STRING\x00', b'true', b'null', b'bool', b'false', b'string\\Leaf'):
        check('wrong-string-' + wrong.hex(), union(cls, names.raw(wrong, 'NIdentifier')), normalized, plain, False)
    check('wrong-string-int', union(cls, names.raw(b'int', 'NIdentifier')), normalized, plain, False)
    check('wrong-string-float', union(cls, names.raw(b'float', 'NIdentifier')), normalized, plain, False)
    for raw_name in (b'', b'_', b'\\Leaf', b'Leaf\\', b'Leaf\\\\Child', b'1Leaf', b'Leaf\x00', b'Leaf-Child',
                     b'self', b'PaReNt', b'STATIC', b'array', b'callable', b'int', b'float', b'string', b'bool',
                     b'object', b'mixed', b'null', b'true', b'false', b'void', b'never', b'iterable', b'Nested\\INT'):
        for kind in ('NName', 'NNameFullyQualified', 'NNameRelative'):
            resolved = raw_name if kind == 'NNameFullyQualified' else b'Def328\\' + raw_name
            check('invalid-class-' + kind + '-' + raw_name.hex(), union(names.raw(raw_name, kind), string), mask(resolved), plain, False)
    for kind in ('NName', 'NNameRelative'):
        check('self-must-not-use-known-scope-' + kind, union(names.raw(b'SeLf', kind), string), mask(b'Def328\\Box323'), plain, False)
    for raw_name in (b'boolean', b'integer', b'double', b'resource'):
        check('plain-confusable-warning-' + raw_name.decode(), union(names.raw(raw_name), string), mask(b'Def328\\' + raw_name), plain, False)
    check('imported-global-underscore-warning', union(names.raw(b'Target328'), string), mask(b'_'),
          names.context(namespace=b'Def328', imports=((b'Target328', b'_'),)), False)
    for label, edited in (
        ('single', cls), ('nullable', 'NNullableType (' + cls + ') eps'),
        ('empty', union()), ('singleton', union(cls)), ('duplicate-string', union(cls, string, string)),
        ('extra-builtin', union(cls, string, names.raw(b'int', 'NIdentifier'))),
        ('extra-class', union(cls, string, names.raw(b'Other'))),
        ('class-Identifier', union(names.raw(b'Leaf', 'NIdentifier'), string)),
        ('intersection', union('NIntersectionType (SEQUENCE ([' + cls + ',' + names.raw(b'Other') + '])) eps', string)),
    ):
        check('raw-shape-' + label, edited, normalized, plain, False)
    for label, edited in (
        ('empty', 'eps'), ('class-only', names.mask(b'Def328\\Leaf')),
        ('string-only', '[' + STRING + ']'),
        ('broadened-bool', normalized.replace('PTBUILTIN "string"', 'PTBUILTIN "bool"')),
        ('wrong-true', normalized.replace('PTBUILTIN "string"', 'PTBUILTIN "true"')),
        ('wrong-null', normalized.replace('PTBUILTIN "string"', 'PTBUILTIN "null"')),
        ('wrong-false', normalized.replace('PTBUILTIN "string"', 'PTBUILTIN "false"')),
        ('extra-string', normalized[:-1] + ',' + STRING + ']'),
        ('builtin', '[(PTBRANCH ([PTBUILTIN "object"])),' + STRING + ']'),
        ('scope', '[(PTBRANCH ([PTSELF])),' + STRING + ']'),
        ('intersection', '[(PTBRANCH ([PTCLASS ([65]),PTCLASS ([66])])),' + STRING + ']'),
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
    print('pass', report['premises'], 'independent class/string assertions, source0')


if __name__ == '__main__':
    main()
