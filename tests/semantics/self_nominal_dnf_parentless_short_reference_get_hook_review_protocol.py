#!/usr/bin/env python3
"""Independent scoped-self DNF grouping, contextual authority and count controls."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import self_parentless_short_reference_get_hook_review_protocol as prior
import self_nominal_pair_parentless_short_reference_get_hook_review_protocol as pair
import self_nominal_union_parentless_short_reference_get_hook_review_protocol as flat
import self_builtin_union_parentless_short_reference_get_hook_review_protocol as builtin
import self_mixed_nominal_union_parentless_short_reference_get_hook_review_protocol as mixed
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
NOMINAL = '$hook_short_reference_nominal_dnf_header'
MIXED = '$hook_short_reference_mixed_nominal_dnf_header'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def assertions():
    rows = []; names = prior.names; owner = b'Def347\\Box347'
    lexical = prior.context(namespace=b'Def347', owner=owner, file=b'original347.php')
    atom = lambda name: 'PTCLASS ' + names.value(name)

    def check(label, raw, parts, expected=True, helper=NOMINAL, ctx=lexical):
        rows.append({'id': label, 'kind': 'header', 'expected': expected,
                     'premise': ('' if expected else '~') + helper + '(' + prior.union(raw) + ',' + prior.branches(parts) + ',' + ctx + ')'})

    def count(label, raw, parts, result, is_mixed=False, ctx=lexical):
        helper = '$hook_short_reference_' + ('mixed_' if is_mixed else '') + 'nominal_dnf_members'
        rows.append({'id': label, 'kind': 'members', 'expected': True,
                     'premise': helper + '(' + ('[' + ','.join(raw) + ']' if raw else 'eps') + ',' +
                     (prior.branches(parts) if parts else 'eps') + ',' + ctx + ') = ' + result})

    for kind in ('NName', 'NNameRelative'):
        self_raw = names.raw(b'SeLf', kind)
        for size in (2, 3, 8):
            classes = [b'Def347\\Arm' + str(i).encode() for i in range(size)]
            conjuncts = [names.raw(name if i % 3 == 2 else b'Arm' + str(i).encode(),
                                    ('NName', 'NNameRelative', 'NNameFullyQualified')[i % 3])
                         for i, name in enumerate(classes)]
            grouped = prior.intersection(conjuncts); conjunction = [atom(name) for name in classes]
            plans = [([self_raw, grouped], [[atom(owner)], conjunction], NOMINAL, 0),
                     ([grouped, self_raw], [conjunction, [atom(owner)]], NOMINAL, 1)]
            integer = names.raw(b'int', 'NIdentifier'); integer_part = ['PTBUILTIN "int"']
            for position in range(3):
                raw = [grouped, integer]; parts = [conjunction, integer_part]
                raw.insert(position, self_raw); parts.insert(position, [atom(owner)])
                plans.append((raw, parts, MIXED, position))
            for index, (raw, parts, helper, position) in enumerate(plans):
                label = kind + '-' + str(size) + '-' + str(index)
                check(label + '-accepted', raw, parts, helper=helper)
                check(label + '-raw-order', list(reversed(raw)), parts, False, helper)
                check(label + '-normalized-order', raw, list(reversed(parts)), False, helper)
                altered = [part.copy() for part in parts]; altered[position] = [atom(owner + b'X')]
                check(label + '-self-bytes', raw, altered, False, helper)
                altered[position] = [atom(owner.swapcase())]
                check(label + '-self-case', raw, altered, False, helper)
                check(label + '-missing-branch', raw, parts[:-1], False, helper)
                check(label + '-extra-branch', raw, parts + [[atom(b'Extra347')]], False, helper)
                group_position = raw.index(grouped)
                changed = raw.copy(); changed[group_position] = prior.intersection(list(reversed(conjuncts)))
                check(label + '-raw-conjunct-order', changed, parts, False, helper)
                altered = [part.copy() for part in parts]; altered[group_position].reverse()
                check(label + '-normalized-conjunct-order', raw, altered, False, helper)
                changed[group_position] = prior.intersection(conjuncts[:-1])
                check(label + '-missing-conjunct', changed, parts, False, helper)
                count(label + '-members', raw, parts, '((1,1))' if helper == MIXED else '(1)', helper == MIXED)

        fq = [names.raw(b'Global347\\A', 'NNameFullyQualified'), names.raw(b'Global347\\B', 'NNameFullyQualified')]
        grouped = prior.intersection(fq); conjunction = [atom(b'Global347\\A'), atom(b'Global347\\B')]
        raw = [self_raw, grouped]; parts = [[atom(owner)], conjunction]
        for helper, extra_raw, extra_parts in ((NOMINAL, [], []), (MIXED, [names.raw(b'null', 'NIdentifier')], [['PTBUILTIN "null"']])):
            prefix = kind + ('-mixed' if helper == MIXED else '-bare')
            selected_raw = raw + extra_raw; selected_parts = parts + extra_parts
            consumer = prior.context(namespace=b'Consumer347', owner=owner, imports=((b'self', b'Foreign347\\Wrong'),))
            check(prefix + '-known-self-independent-of-consumer', selected_raw, selected_parts, helper=helper, ctx=consumer)
            for scope in ('PTGLOBAL', 'PTDEFERRED', 'PTANONYMOUS true', 'PTANONYMOUS false',
                          'PTTRAIT ' + names.value(b'Def347\\Trait347'),
                          'PTKNOWN ' + names.value(b'Wrong347\\Box347') + ' eps'):
                check(prefix + '-wrong-scope-' + scope, selected_raw, selected_parts, False, helper,
                      prior.context(namespace=b'Def347', owner=owner, scope=scope))
            for label, ctx in (('missing-file', prior.context(namespace=b'Def347', owner=owner, file=b'')),
                               ('missing-line', prior.context(namespace=b'Def347', owner=owner, line=0))):
                check(prefix + '-' + label, selected_raw, selected_parts, False, helper, ctx)
            for wrong_kind in ('NIdentifier', 'NNameFullyQualified'):
                check(prefix + '-wrong-self-kind-' + wrong_kind, [names.raw(b'self', wrong_kind), grouped] + extra_raw,
                      selected_parts, False, helper)
            for keyword in (b'parent', b'static', b'_', b'boolean', b'1Bad', b'Bad\x00'):
                check(prefix + '-wrong-singleton-' + keyword.hex(), [names.raw(keyword, kind), grouped] + extra_raw,
                      selected_parts, False, helper)
            check(prefix + '-duplicate-owner', selected_raw + [names.raw(owner, 'NNameFullyQualified')],
                  selected_parts + [[atom(owner)]], False, helper)
            check(prefix + '-subsumed-conjunction', selected_raw + [fq[0]], selected_parts + [[conjunction[0]]], False, helper)
            check(prefix + '-self-inside-conjunction-unchanged',
                  [prior.intersection([self_raw, fq[0]]), fq[1]] + extra_raw,
                  [[atom(owner), conjunction[0]], [conjunction[1]]] + extra_parts, False, helper)
            check(prefix + '-no-intersection', [self_raw, fq[0]] + extra_raw,
                  [[atom(owner)], [conjunction[0]]] + extra_parts, False, helper)
            check(prefix + '-singleton-conjunction', [self_raw, prior.intersection(fq[:1])] + extra_raw,
                  [[atom(owner)], [conjunction[0]]] + extra_parts, False, helper)
            ordinary = [names.raw(b'LocalA'), names.raw(b'LocalB', 'NNameRelative')]
            check(prefix + '-ordinary-conjuncts-use-defining-namespace',
                  [self_raw, prior.intersection(ordinary)] + extra_raw,
                  [[atom(owner)], [atom(b'Def347\\LocalA'), atom(b'Def347\\LocalB')]] + extra_parts, False, helper, consumer)
        count(kind + '-empty-members', [], [], '(0)')
        count(kind + '-empty-mixed-members', [], [], '((0,0))', True)
        count(kind + '-self-is-not-intersection', [self_raw], [[atom(owner)]], '(0)')
        count(kind + '-self-is-not-builtin', [self_raw], [[atom(owner)]], '((0,0))', True)

    affected = 0
    for label, module in (('pair', pair), ('flat', flat), ('builtin', builtin)):
        for original in module.assertions():
            if 'dnf' in original['id'].lower() and (NOMINAL + '(' in original['premise'] or MIXED + '(' in original['premise']):
                assert original['expected'] is True and not original['premise'].startswith('~')
                rows.append({**original, 'id': 'current-' + label + '-' + original['id'],
                             'kind': 'affected-current-query'})
                affected += 1
    retained = [row for row in mixed.assertions() if row['id'].endswith('-DNF-unchanged')]
    assert len(retained) == 2 and all(row['expected'] is False and row['premise'].startswith('~') for row in retained)
    rows += [{**row, 'id': 'retained-intersection-' + row['id'], 'kind': 'retained-intersection-query'} for row in retained]
    assert affected == 10
    assert len({row['id'] for row in rows}) == len(rows)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), *(Path(module.__file__) for module in (prior, prior.names, pair, flat, builtin, mixed)),
             ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'spec/semantics/modules.json',
             ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *modules]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'mode': 'fixture-SL',
              'source_agreement_credit': 0, 'native_observations': 0, 'affected_current_queries': 10,
              'retained_intersection_queries': 2, 'passed': False}
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
    print('pass', report['premises'], 'independent scoped-self DNF assertions, source0')


if __name__ == '__main__':
    main()
