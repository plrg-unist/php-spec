#!/usr/bin/env python3
"""Independent scoped-self flat nominal-fold order and boundary controls."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import self_parentless_short_reference_get_hook_review_protocol as prior
import nominal_union_parentless_short_reference_get_hook_review_protocol as legacy
import self_nominal_pair_parentless_short_reference_get_hook_review_protocol as pair
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
HELPER = '$hook_short_reference_nominal_union_header'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def assertions():
    rows = []; names = prior.names; owner = b'Def344\\Box344'
    lexical = prior.context(namespace=b'Def344', owner=owner, file=b'original344.php')
    union = lambda raw: prior.union(raw)
    mask = lambda classes: prior.branches([['PTCLASS ' + names.value(name)] for name in classes])

    def check(label, raw, typed, context=lexical, expected=True, helper=HELPER):
        rows.append({'id': label, 'expected': expected, 'premise': ('' if expected else '~') +
                     helper + '(' + raw + ',' + typed + ',' + context + ')'})

    for kind in ('NName', 'NNameRelative'):
        self_raw = names.raw(b'SeLf', kind)
        for length in (3, 4, 8):
            for position in sorted({0, length // 2, length - 1}):
                raw = []; classes = []
                for index in range(length - 1):
                    name = ('Arm' + str(index)).encode()
                    raw_kind = ('NName', 'NNameRelative', 'NNameFullyQualified')[index % 3]
                    raw.append(names.raw(name, raw_kind))
                    classes.append(name if raw_kind == 'NNameFullyQualified' else b'Def344\\' + name)
                raw.insert(position, self_raw); classes.insert(position, owner)
                ast = union(raw); typed = mask(classes); label = kind + '-' + str(length) + '-' + str(position)
                check(label, ast, typed)
                check(label + '-raw-order', union(list(reversed(raw))), typed, expected=False)
                check(label + '-normalized-order', ast, mask(list(reversed(classes))), expected=False)
                altered = classes.copy(); altered[position] += b'X'
                check(label + '-self-bytes', ast, mask(altered), expected=False)
                altered = classes.copy(); altered[position] = altered[position].swapcase()
                check(label + '-self-case', ast, mask(altered), expected=False)
                check(label + '-missing-type', ast, mask(classes[:-1]), expected=False)
                check(label + '-pair-stays-excluded', ast, typed, expected=False,
                      helper='$hook_short_reference_nominal_pair_header')
        other_raw = [names.raw(b'First', 'NNameFullyQualified'), names.raw(b'Second', 'NNameFullyQualified')]
        ast = union([self_raw, *other_raw]); typed = mask([owner, b'First', b'Second'])
        check(kind + '-extra-normalized-arm', ast, mask([owner, b'First', b'Second', b'Extra']), expected=False)
        consumer = prior.context(namespace=b'Consumer344', owner=owner,
                                 imports=((b'self', b'Foreign344\\Wrong'), (b'First', b'stdClass')))
        check(kind + '-known-self-survives-consumer-namespace-and-alias', ast, typed, consumer)
        check(kind + '-ordinary-other-does-not-use-consumer-context',
              union([self_raw, names.raw(b'First'), other_raw[1]]),
              mask([owner, b'Def344\\First', b'Second']), consumer, False)
        for scope in ('PTGLOBAL', 'PTDEFERRED', 'PTANONYMOUS true', 'PTANONYMOUS false',
                      'PTTRAIT ' + names.value(b'Def344\\Trait344'),
                      'PTKNOWN ' + names.value(b'Wrong344\\Box344') + ' eps'):
            check(kind + '-wrong-scope-' + scope, ast, typed,
                  prior.context(namespace=b'Def344', owner=owner, scope=scope), False)
        check(kind + '-missing-file', ast, typed, prior.context(namespace=b'Def344', owner=owner, file=b''), False)
        check(kind + '-missing-line', ast, typed, prior.context(namespace=b'Def344', owner=owner, line=0), False)
        parent_scope = 'PTKNOWN ' + names.value(owner) + ' (' + names.value(b'Def344\\Parent344') + ')'
        parent_context = prior.context(namespace=b'Def344', owner=owner, scope=parent_scope)
        parent_raw = union([names.raw(b'parent', kind), *other_raw])
        parent_type = mask([b'Def344\\Parent344', b'First', b'Second'])
        rows.append({'id': kind + '-known-parent-normalizes', 'expected': True,
                     'premise': '$ptype_normalize(' + parent_raw + ',' + parent_context + ') = PTOK (' + parent_type + ') eps'})
        check(kind + '-known-parent-stays-excluded', parent_raw, parent_type, parent_context, False)
        check(kind + '-duplicate-self', union([self_raw, names.raw(b'self'), other_raw[0]]),
              mask([owner, owner, b'First']), expected=False)
        check(kind + '-duplicate-owner', union([self_raw, names.raw(owner, 'NNameFullyQualified'), other_raw[0]]),
              mask([owner, owner, b'First']), expected=False)
        for name in (b'_', b'parent', b'static', b'int', b'callable', b'boolean', b'1Bad', b'Bad\x00'):
            check(kind + '-bad-other-' + name.hex(), union([self_raw, names.raw(name), other_raw[0]]),
                  mask([owner, b'Def344\\' + name, b'First']), expected=False)
        for wrong_kind in ('NIdentifier', 'NNameFullyQualified'):
            check(kind + '-wrong-self-kind-' + wrong_kind, union([names.raw(b'self', wrong_kind), *other_raw]), typed, expected=False)
        check(kind + '-only-two', union([self_raw, other_raw[0]]), mask([owner, b'First']), expected=False)
        intersection = prior.intersection([self_raw, other_raw[0]])
        inter_type = prior.branches([['PTCLASS ' + names.value(owner), 'PTCLASS ' + names.value(b'First')]])
        check(kind + '-intersection-admitted', intersection, inter_type, expected=True,
              helper='$hook_short_reference_nominal_intersection_header')
        grouped = prior.intersection(other_raw)
        dnf = prior.branches([['PTCLASS ' + names.value(b'First'), 'PTCLASS ' + names.value(b'Second')], ['PTCLASS ' + names.value(owner)]])
        check(kind + '-dnf-unchanged', union([grouped, self_raw]), dnf, expected=True,
              helper='$hook_short_reference_nominal_dnf_header')
        mixed = prior.branches([['PTCLASS ' + names.value(owner)], ['PTCLASS ' + names.value(b'First')], ['PTBUILTIN "int"']])
        check(kind + '-mixed-union-unchanged', union([self_raw, other_raw[0], names.raw(b'int', 'NIdentifier')]), mixed,
              expected=False, helper='$hook_short_reference_mixed_nominal_union_header')
        builtins = prior.branches([['PTCLASS ' + names.value(owner)], ['PTBUILTIN "int"'], ['PTBUILTIN "null"']])
        check(kind + '-class-builtin-union-unchanged', union([self_raw, names.raw(b'int', 'NIdentifier'), names.raw(b'null', 'NIdentifier')]),
              builtins, expected=False, helper='$hook_short_reference_class_builtin_union_header')
        mixed_dnf = prior.branches([['PTCLASS ' + names.value(b'First'), 'PTCLASS ' + names.value(b'Second')],
                                    ['PTCLASS ' + names.value(owner)], ['PTBUILTIN "int"']])
        check(kind + '-mixed-dnf-unchanged', union([grouped, self_raw, names.raw(b'int', 'NIdentifier')]), mixed_dnf,
              expected=True, helper='$hook_short_reference_mixed_nominal_dnf_header')

    for kind in ('NName', 'NNameRelative'):
        original = next(row for row in pair.assertions() if row['id'] == kind + '-larger-fold-accepted')
        rows.append({**original, 'id': 'promoted-old343-' + kind + '-larger-fold'})
    for original in legacy.assertions():
        if original['id'] in ('members-empty-base', 'members-empty-raw', 'members-empty-normalized'):
            rows.append({**original, 'id': 'adapted-old334-' + original['id']})
    assert sum(row['id'].startswith('adapted-old334-') for row in rows) == 3
    assert len({row['id'] for row in rows}) == len(rows)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(prior.__file__), Path(legacy.__file__), Path(pair.__file__), Path(prior.names.__file__),
             ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'spec/semantics/modules.json',
             ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *modules]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'mode': 'fixture-SL',
              'source_agreement_credit': 0, 'native_observations': 0, 'promoted_old343_queries': 2,
              'adapted_old334_member_calls': 3, 'passed': False}
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
    print('pass', report['premises'], 'independent scoped-self nominal-fold assertions, source0')


if __name__ == '__main__':
    main()
