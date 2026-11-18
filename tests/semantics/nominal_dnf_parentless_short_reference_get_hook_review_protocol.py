#!/usr/bin/env python3
"""Independent nominal DNF grouping, order and contextual type controls."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import scoped_class_parentless_short_reference_get_hook_review_protocol as names
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
HELPER = '$hook_short_reference_nominal_dnf_header'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def intersection(raw):
    return 'NIntersectionType (SEQUENCE ' + ('([' + ','.join(raw) + '])' if raw else 'eps') + ') eps'


def arm(raw):
    return raw[0] if len(raw) == 1 else intersection(raw)


def union(arms):
    return 'NUnionType (SEQUENCE ' + ('([' + ','.join(arms) + '])' if arms else 'eps') + ') eps'


def normalized(branches):
    return '[' + ','.join('(PTBRANCH ([' + ','.join('PTCLASS ' + names.value(name) for name in branch) + ']))' for branch in branches) + ']' if branches else 'eps'


def assertions():
    rows = []
    context = names.context(namespace=b'Dnf339', file=b'original339.php')

    def check(label, raw, branches, expected, lexical=context):
        rows.append({'id': label, 'expected': expected,
                     'premise': ('' if expected else '~') + HELPER + '(' + union(raw) + ',' + branches + ',' + lexical + ')'})

    plans = ((2, 1), (1, 2), (2, 2), (3, 2), (2, 1, 2), (8, 1), (17, 1), (2,) + (1,) * 7, (2,) + (1,) * 16)
    for sizes in plans:
        for offset in range(3):
            short = [[('Arm' + str(i) + '_' + str(j)).encode() for j in range(size)] for i, size in enumerate(sizes)]
            resolved = [[b'Dnf339\\' + name for name in branch] for branch in short]
            raw = [[names.raw(value if (i + j + offset) % 3 == 2 else name,
                              ('NName', 'NNameRelative', 'NNameFullyQualified')[(i + j + offset) % 3])
                    for j, (name, value) in enumerate(zip(branch, resolved[i]))] for i, branch in enumerate(short)]
            rawarms = [arm(branch) for branch in raw]; branch = normalized(resolved)
            label = '-'.join(map(str, sizes)) + '-' + str(offset)
            check(label + '-accepted', rawarms, branch, True)
            check(label + '-raw-branch-order', list(reversed(rawarms)), branch, False)
            check(label + '-normalized-branch-order', rawarms, normalized(list(reversed(resolved))), False)
            first = next(i for i, size in enumerate(sizes) if size >= 2)
            altered = rawarms.copy(); altered[first] = arm(list(reversed(raw[first])))
            check(label + '-raw-atom-order', altered, branch, False)
            values = [part.copy() for part in resolved]; values[first].reverse()
            check(label + '-normalized-atom-order', rawarms, normalized(values), False)
            check(label + '-missing-raw-branch', rawarms[:-1], branch, False)
            check(label + '-missing-normalized-branch', rawarms, normalized(resolved[:-1]), False)
            check(label + '-extra-normalized-branch', rawarms, normalized(resolved + [[b'Dnf339\\Extra']]), False)
            flattened = [name for part in resolved for name in part]
            check(label + '-flatten-conjunction', rawarms, normalized([flattened]), False)
            check(label + '-split-union', rawarms, normalized([[name] for name in flattened]), False)
            for position in sorted({0, len(resolved[first]) // 2, len(resolved[first]) - 1}):
                values = [part.copy() for part in resolved]; values[first][position] += b'X'
                check(label + '-corrupt-' + str(position), rawarms, normalized(values), False)

    raw = [names.raw(b'A'), names.raw(b'B'), names.raw(b'C')]
    values = [b'Dnf339\\A', b'Dnf339\\B', b'Dnf339\\C']
    ordinary = [intersection(raw[:2]), raw[2]]; good = normalized([values[:2], values[2:]])
    check('empty-union', [], 'eps', False)
    check('singleton-union', ordinary[:1], normalized([values[:2]]), False)
    check('pure-flat-union', [raw[0], raw[1]], normalized([[values[0]], [values[1]]]), False)
    check('empty-intersection', [intersection([]), raw[2]], good, False)
    check('singleton-intersection', [intersection(raw[:1]), raw[2]], normalized([[values[0]], values[2:]]), False)
    check('empty-normalized', ordinary, 'eps', False)
    check('empty-normalized-branch', ordinary, '[(PTBRANCH eps),(PTBRANCH ([PTCLASS ' + names.value(values[2]) + ']))]', False)
    for builtin in ('array', 'int', 'float', 'string', 'null', 'bool', 'false', 'true', 'iterable', 'object', 'mixed', 'void', 'never'):
        check('builtin-branch-' + builtin, [ordinary[0], names.raw(builtin.encode(), 'NIdentifier')],
              '[' + normalized([values[:2]])[1:-1] + ',(PTBRANCH ([PTBUILTIN "' + builtin + '"]))]', False)
        check('builtin-intersection-' + builtin, [intersection([raw[0], names.raw(builtin.encode(), 'NIdentifier')]), raw[2]], good, False)
    for atom in ('PTSELF', 'PTPARENT', 'PTSTATIC', 'PTBUILTIN "object"'):
        check('nonclass-normalized-' + atom, ordinary, good.replace('PTCLASS ' + names.value(values[0]), atom, 1), False)
    for text in (b'', b'_', b'1Name', b'Name\x00', b'self', b'parent', b'static'):
        check('invalid-name-' + text.hex(), [intersection([names.raw(text), raw[1]]), raw[2]], good, False)
    for text in (b'boolean', b'integer', b'double', b'resource'):
        check('nonquiet-' + text.decode(), [intersection([names.raw(text), raw[1]]), raw[2]],
              normalized([[b'Dnf339\\' + text, values[1]], values[2:]]), False)
    check('identifier-as-class', [intersection([names.raw(b'A', 'NIdentifier'), raw[1]]), raw[2]], good, False)
    check('case-duplicate-conjunct', [intersection([raw[0], names.raw(b'a')]), raw[2]], normalized([[values[0], b'Dnf339\\a'], values[2:]]), False)
    check('duplicate-branch', [ordinary[0], intersection(list(reversed(raw[:2])))], normalized([values[:2], list(reversed(values[:2]))]), False)
    for reverse in (False, True):
        branches = [ordinary[0], raw[0]]; targets = [values[:2], values[:1]]
        if reverse: branches.reverse(); targets.reverse()
        check('subsumed-' + str(reverse), branches, normalized(targets), False)
    check('shared-atom-legal', [ordinary[0], intersection([raw[0], raw[2]])], normalized([values[:2], [values[0], values[2]]]), True)
    imported = names.context(namespace=b'Dnf339', file=b'original339.php', imports=((b'Alpha', b'Payload339\\A'), (b'Tree', b'Payload339'), (b'Gamma', b'Payload339\\C'), (b'Other', b'Payload339\\A')))
    aliasraw = [names.raw(b'gAmMa'), intersection([names.raw(b'tReE\\B'), names.raw(b'aLpHa')])]
    aliastypes = [[b'Payload339\\C'], [b'Payload339\\B', b'Payload339\\A']]
    check('imported-single-first', aliasraw, normalized(aliastypes), True, imported)
    check('imported-consumer-shadow', aliasraw, normalized(aliastypes), False)
    check('imported-duplicate-conjunct', [intersection([names.raw(b'Alpha'), names.raw(b'Other')]), names.raw(b'Gamma')], normalized([[b'Payload339\\A'] * 2, [b'Payload339\\C']]), False, imported)
    check('imported-subsumed-branch', [names.raw(b'Other'), intersection([names.raw(b'Alpha'), names.raw(b'Tree\\B')])], normalized([[b'Payload339\\A'], [b'Payload339\\A', b'Payload339\\B']]), False, imported)
    for label, lexical in (('wrong-namespace', names.context(namespace=b'Consumer339', file=b'original339.php')),
                           ('missing-file', names.context(namespace=b'Dnf339', file=b'')),
                           ('missing-line', names.context(namespace=b'Dnf339', file=b'original339.php', line=0))):
        check(label, ordinary, good, False, lexical)
    rows.append({'id': 'bare-intersection-not-dnf', 'expected': False,
                 'premise': '~' + HELPER + '(' + ordinary[0] + ',' + normalized([values[:2]]) + ',' + context + ')'})
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
    print('pass', report['premises'], 'independent nominal DNF assertions, source0')


if __name__ == '__main__':
    main()
