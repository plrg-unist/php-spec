#!/usr/bin/env python3
"""Independent nominal intersection order, shape and namespace controls."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import scoped_class_parentless_short_reference_get_hook_review_protocol as names
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
HELPER = '$hook_short_reference_nominal_intersection_header'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def intersection(raw):
    return 'NIntersectionType (SEQUENCE ' + ('([' + ','.join(raw) + '])' if raw else 'eps') + ') eps'


def atoms(values):
    return '([' + ','.join('PTCLASS ' + names.value(value) for value in values) + '])' if values else 'eps'


def normalized(values):
    return '[(PTBRANCH ' + atoms(values) + ')]'


def assertions():
    rows = []
    context = names.context(namespace=b'Intersect338', file=b'original338.php')

    def check(label, raw, branches, expected, lexical=context):
        rows.append({'id': label, 'expected': expected,
                     'premise': ('' if expected else '~') + HELPER + '(' + intersection(raw) + ',' + branches + ',' + lexical + ')'})

    for size in (2, 3, 4, 8, 17):
        short = [('Arm' + str(i)).encode() for i in range(size)]
        resolved = [b'Intersect338\\' + name for name in short]
        for offset in range(3):
            kinds = [('NName', 'NNameRelative', 'NNameFullyQualified')[(i + offset) % 3] for i in range(size)]
            raw = [names.raw(value if kind == 'NNameFullyQualified' else name, kind)
                   for name, value, kind in zip(short, resolved, kinds)]
            label = str(size) + '-' + str(offset)
            branch = normalized(resolved)
            check(label + '-accepted', raw, branch, True)
            check(label + '-raw-order', list(reversed(raw)), branch, False)
            check(label + '-normalized-order', raw, normalized(list(reversed(resolved))), False)
            check(label + '-missing', raw, normalized(resolved[:-1]), False)
            check(label + '-extra', raw, normalized(resolved + [b'Intersect338\\Extra']), False)
            split = '[' + ','.join('(PTBRANCH ' + atoms([value]) + ')' for value in resolved) + ']'
            check(label + '-split-union', raw, split, False)
            check(label + '-extra-branch', raw, '[' + '(PTBRANCH ' + atoms(resolved) + '),(PTBRANCH ' + atoms([b'Extra']) + ')]', False)
            for position in sorted({0, size // 2, size - 1}):
                altered = resolved.copy(); altered[position] += b'X'
                check(label + '-corrupt-' + str(position), raw, normalized(altered), False)

    raw = [names.raw(b'First'), names.raw(b'Last')]
    resolved = [b'Intersect338\\First', b'Intersect338\\Last']
    check('empty-raw', [], normalized([]), False)
    check('singleton', raw[:1], normalized(resolved[:1]), False)
    check('empty-normalized', raw, 'eps', False)
    check('empty-branch', raw, normalized([]), False)
    for atom in ('PTSELF', 'PTPARENT', 'PTSTATIC', 'PTBUILTIN "object"', 'PTBUILTIN "int"'):
        check('nonclass-' + atom, raw, '[(PTBRANCH ([PTCLASS ' + names.value(resolved[0]) + ',' + atom + ']))]', False)
    for position in range(2):
        for value in (b'', b'_', b'1Name', b'Name\x00', b'self', b'parent', b'static', b'int', b'array'):
            altered = raw.copy(); altered[position] = names.raw(value)
            check('bad-name-' + str(position) + '-' + value.hex(), altered, normalized(resolved), False)
        altered = raw.copy(); altered[position] = names.raw(b'First', 'NIdentifier')
        check('identifier-nominal-' + str(position), altered, normalized(resolved), False)
        for value in (b'boolean', b'integer', b'double', b'resource'):
            altered = raw.copy(); altered[position] = names.raw(value)
            target = resolved.copy(); target[position] = b'Intersect338\\' + value
            check('nonquiet-' + str(position) + '-' + value.decode(), altered, normalized(target), False)
    for builtin in ('array', 'int', 'float', 'string', 'null', 'bool', 'iterable', 'object', 'mixed', 'void', 'never'):
        check('builtin-' + builtin, [raw[0], names.raw(builtin.encode(), 'NIdentifier')],
              '[(PTBRANCH ([PTCLASS ' + names.value(resolved[0]) + ',PTBUILTIN "' + builtin + '"]))]', False)
    check('case-duplicate', [raw[0], names.raw(b'fIrSt')], normalized([resolved[0], b'Intersect338\\fIrSt']), False)
    imported = names.context(namespace=b'Intersect338', file=b'original338.php',
                             imports=((b'Alpha', b'Payload338\\A'), (b'Tree', b'Payload338')))
    aliasraw = [names.raw(b'aLpHa'), names.raw(b'tReE\\B')]
    aliasresolved = [b'Payload338\\A', b'Payload338\\B']
    check('imported', aliasraw, normalized(aliasresolved), True, imported)
    check('imported-consumer-shadow', aliasraw, normalized(aliasresolved), False)
    duplicate = names.context(namespace=b'Intersect338', file=b'original338.php',
                              imports=((b'Left', b'Payload338\\A'), (b'Right', b'Payload338\\A')))
    check('alias-duplicate', [names.raw(b'Left'), names.raw(b'Right')], normalized([b'Payload338\\A'] * 2), False, duplicate)
    for label, lexical in (('wrong-namespace', names.context(namespace=b'Consumer338', file=b'original338.php')),
                           ('missing-file', names.context(namespace=b'Intersect338', file=b'')),
                           ('missing-line', names.context(namespace=b'Intersect338', file=b'original338.php', line=0))):
        check(label, raw, normalized(resolved), False, lexical)
    top = 'NUnionType (SEQUENCE ([' + ','.join(raw) + '])) eps'
    rows.append({'id': 'union-not-intersection', 'expected': False,
                 'premise': '~' + HELPER + '(' + top + ',' + normalized(resolved) + ',' + context + ')'})
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
    print('pass', report['premises'], 'independent nominal intersection assertions, source0')


if __name__ == '__main__':
    main()
