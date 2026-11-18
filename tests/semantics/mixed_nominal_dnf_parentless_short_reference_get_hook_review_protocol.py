#!/usr/bin/env python3
"""Independent mixed DNF grouping, builtin and contextual type controls."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import scoped_class_parentless_short_reference_get_hook_review_protocol as names
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
HELPER = '$hook_short_reference_mixed_nominal_dnf_header'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def intersection(raw):
    return 'NIntersectionType (SEQUENCE ' + ('([' + ','.join(raw) + '])' if raw else 'eps') + ') eps'


def union(raw):
    return 'NUnionType (SEQUENCE ' + ('([' + ','.join(raw) + '])' if raw else 'eps') + ') eps'


def normalized(branches):
    def branch(value):
        atoms = ['PTBUILTIN "' + value + '"'] if isinstance(value, str) else ['PTCLASS ' + names.value(name) for name in value]
        return '(PTBRANCH (' + ('[' + ','.join(atoms) + ']' if atoms else 'eps') + '))'
    return '[' + ','.join(branch(value) for value in branches) + ']' if branches else 'eps'


def assertions():
    rows = []
    context = names.context(namespace=b'Mixed340', file=b'original340.php')

    def check(label, raw, branches, expected, lexical=context):
        rows.append({'id': label, 'expected': expected,
                     'premise': ('' if expected else '~') + HELPER + '(' + union(raw) + ',' + branches + ',' + lexical + ')'})

    domain = ('array', 'int', 'float', 'string', 'null', 'bool', 'false', 'true')
    for number, builtin in enumerate(domain):
        size = (2, 3, 8, 17)[number % 4]
        short = [('Arm' + str(i)).encode() for i in range(size)]
        values = [b'Mixed340\\' + name for name in short]
        raw = [names.raw(value if (i + number) % 3 == 2 else name,
                         ('NName', 'NNameRelative', 'NNameFullyQualified')[(i + number) % 3])
               for i, (name, value) in enumerate(zip(short, values))]
        for reverse in (False, True):
            rawarms = [intersection(raw), names.raw(builtin.encode(), 'NIdentifier')]
            resolved = [values, builtin]
            if reverse: rawarms.reverse(); resolved.reverse()
            slot = 1 if reverse else 0; label = builtin + '-' + str(reverse)
            check(label + '-accepted', rawarms, normalized(resolved), True)
            upper = rawarms.copy(); upper[1 - slot] = names.raw(builtin.upper().encode(), 'NIdentifier')
            check(label + '-uppercase-builtin', upper, normalized(resolved), True)
            check(label + '-raw-branch-order', list(reversed(rawarms)), normalized(resolved), False)
            check(label + '-normalized-branch-order', rawarms, normalized(list(reversed(resolved))), False)
            altered = rawarms.copy(); altered[slot] = intersection(list(reversed(raw)))
            check(label + '-raw-conjunct-order', altered, normalized(resolved), False)
            target = resolved.copy(); target[slot] = list(reversed(values))
            check(label + '-normalized-conjunct-order', rawarms, normalized(target), False)
            check(label + '-drop-builtin', [intersection(raw)], normalized([values]), False)
            check(label + '-drop-conjunction', [names.raw(builtin.encode(), 'NIdentifier')], normalized([builtin]), False)
            target = resolved.copy(); target[1 - slot] = 'int' if builtin != 'int' else 'array'
            check(label + '-wrong-builtin-mask', rawarms, normalized(target), False)
            target = [[value] for value in values] + [builtin]
            check(label + '-split-conjunction', rawarms, normalized(target), False)
            check(label + '-extra-branch', rawarms, normalized(resolved + [[b'Mixed340\\Extra']]), False)
            wrong = rawarms.copy(); wrong[1 - slot] = names.raw(builtin.encode(), 'NName')
            check(label + '-builtin-name-kind', wrong, normalized(resolved), False)
            for position in sorted({0, size // 2, size - 1}):
                target = resolved.copy(); target[slot] = values.copy(); target[slot][position] += b'X'
                check(label + '-corrupt-' + str(position), rawarms, normalized(target), False)

    raw = [names.raw(b'A'), names.raw(b'B')]; values = [b'Mixed340\\A', b'Mixed340\\B']; grouped = intersection(raw)
    combinations = (('array', 'null'), ('int', 'float'), ('string', 'bool'), ('false', 'null'), ('true', 'null'), ('array', 'int', 'float', 'string', 'bool', 'null'))
    for kinds in combinations:
        builtins = [names.raw(kind.encode(), 'NIdentifier') for kind in kinds]
        check('compatible-' + '-'.join(kinds), [grouped, *builtins], normalized([values, *kinds]), True)
        check('compatible-reversed-' + '-'.join(kinds), list(reversed([grouped, *builtins])), normalized(list(reversed([values, *kinds]))), True)
    for kinds in (('bool', 'false'), ('bool', 'true'), ('false', 'true'), ('int', 'int'), ('array', 'array')):
        check('incompatible-' + '-'.join(kinds), [grouped, *(names.raw(kind.encode(), 'NIdentifier') for kind in kinds)], normalized([values, *kinds]), False)
    extras = [[('Extra' + str(i)).encode()] for i in range(14)]
    check('seventeen-branches', [grouped, names.raw(b'int', 'NIdentifier'), *(names.raw(value[0]) for value in extras), names.raw(b'Last')],
          normalized([values, 'int', *[[b'Mixed340\\' + value[0]] for value in extras], [b'Mixed340\\Last']]), True)
    check('two-intersections', [grouped, names.raw(b'null', 'NIdentifier'), intersection([names.raw(b'C'), names.raw(b'D')])],
          normalized([values, 'null', [b'Mixed340\\C', b'Mixed340\\D']]), True)
    check('shared-atom', [grouped, names.raw(b'int', 'NIdentifier'), intersection([raw[0], names.raw(b'C')])], normalized([values, 'int', [values[0], b'Mixed340\\C']]), True)
    check('no-builtin', [grouped, names.raw(b'C')], normalized([values, [b'Mixed340\\C']]), False)
    check('no-intersection', [raw[0], names.raw(b'int', 'NIdentifier')], normalized([[values[0]], 'int']), False)
    check('empty', [], 'eps', False)
    check('empty-conjunction', [intersection([]), names.raw(b'int', 'NIdentifier')], normalized([[], 'int']), False)
    check('singleton-conjunction', [intersection(raw[:1]), names.raw(b'int', 'NIdentifier')], normalized([values[:1], 'int']), False)
    check('empty-normalized', [grouped, names.raw(b'int', 'NIdentifier')], 'eps', False)
    for builtin in ('object', 'iterable', 'mixed', 'callable', 'void', 'never', 'integer'):
        check('excluded-' + builtin, [grouped, names.raw(builtin.encode(), 'NIdentifier')], normalized([values, builtin]), False)
    for text in (b'', b'_', b'1Name', b'Name\x00', b'self', b'parent', b'static', b'int'):
        check('bad-conjunct-' + text.hex(), [intersection([names.raw(text), raw[1]]), names.raw(b'int', 'NIdentifier')], normalized([values, 'int']), False)
    for text in (b'boolean', b'integer', b'double', b'resource'):
        check('nonquiet-' + text.decode(), [intersection([names.raw(text), raw[1]]), names.raw(b'int', 'NIdentifier')], normalized([[b'Mixed340\\' + text, values[1]], 'int']), False)
    check('duplicate-conjunct', [intersection([raw[0], names.raw(b'a')]), names.raw(b'int', 'NIdentifier')], normalized([[values[0], b'Mixed340\\a'], 'int']), False)
    check('subsumed-conjunction', [grouped, raw[0], names.raw(b'int', 'NIdentifier')], normalized([values, values[:1], 'int']), False)
    imported = names.context(namespace=b'Mixed340', file=b'original340.php', imports=((b'Alpha', b'Payload340\\A'), (b'Tree', b'Payload340')))
    aliasraw = [names.raw(b'int', 'NIdentifier'), intersection([names.raw(b'tReE\\B'), names.raw(b'aLpHa')])]
    aliastypes = ['int', [b'Payload340\\B', b'Payload340\\A']]
    check('imported', aliasraw, normalized(aliastypes), True, imported)
    check('consumer-shadow', aliasraw, normalized(aliastypes), False)
    for label, lexical in (('wrong-namespace', names.context(namespace=b'Consumer340', file=b'original340.php')),
                           ('missing-file', names.context(namespace=b'Mixed340', file=b'')),
                           ('missing-line', names.context(namespace=b'Mixed340', file=b'original340.php', line=0))):
        check(label, [grouped, names.raw(b'int', 'NIdentifier')], normalized([values, 'int']), False, lexical)
    rows.append({'id':'bare-intersection', 'expected':False,'premise':'~' + HELPER + '(' + grouped + ',' + normalized([values]) + ',' + context + ')'})
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
    print('pass', report['premises'], 'independent mixed nominal DNF assertions, source0')


if __name__ == '__main__':
    main()
