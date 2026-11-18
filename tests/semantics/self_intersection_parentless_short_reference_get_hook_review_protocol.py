#!/usr/bin/env python3
"""Independent scoped-self conjunct order, authority and whole-header guards."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import self_parentless_short_reference_get_hook_review_protocol as prior
import relative_self_parentless_short_reference_get_hook_review_protocol as relative
import self_nominal_pair_parentless_short_reference_get_hook_review_protocol as pair
import self_nominal_union_parentless_short_reference_get_hook_review_protocol as flat
import self_builtin_union_parentless_short_reference_get_hook_review_protocol as builtin
import self_mixed_nominal_union_parentless_short_reference_get_hook_review_protocol as mixed
import self_nominal_dnf_parentless_short_reference_get_hook_review_protocol as dnf
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
INTERSECTION = '$hook_short_reference_nominal_intersection_header'
NOMINAL = '$hook_short_reference_nominal_dnf_header'
MIXED = '$hook_short_reference_mixed_nominal_dnf_header'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def assertions():
    rows = []; names = prior.names; owner = b'Def348\\Box348'
    lexical = prior.context(namespace=b'Def348', owner=owner, file=b'original348.php')
    atom = lambda name: 'PTCLASS ' + names.value(name)

    def check(label, raw, parts, expected=True, helper=INTERSECTION, ctx=lexical):
        rows.append({'id': label, 'kind': 'header', 'expected': expected,
                     'premise': ('' if expected else '~') + helper + '(' + raw + ',' + prior.branches(parts) + ',' + ctx + ')'})

    for kind in ('NName', 'NNameRelative'):
        selfraw = names.raw(b'SeLf', kind)
        for size in (2, 3, 8):
            for position in sorted({0, size // 2, size - 1}):
                raw = []; atoms = []
                for i in range(size - 1):
                    name = b'Arm' + str(i).encode(); rawkind = ('NName', 'NNameRelative', 'NNameFullyQualified')[i % 3]
                    raw.append(names.raw(name, rawkind)); atoms.append(atom(name if rawkind == 'NNameFullyQualified' else b'Def348\\' + name))
                raw.insert(position, selfraw); atoms.insert(position, atom(owner))
                group = prior.intersection(raw); other = names.raw(b'Other348', 'NNameFullyQualified')
                plans = [(INTERSECTION, group, [atoms]),
                         (NOMINAL, prior.union([group, other]), [atoms, [atom(b'Other348')]]),
                         (MIXED, prior.union([names.raw(b'null', 'NIdentifier'), group]), [['PTBUILTIN "null"'], atoms])]
                for helper, ast, parts in plans:
                    label = kind + '-' + str(size) + '-' + str(position) + '-' + helper.removeprefix('$hook_short_reference_').removesuffix('_header')
                    check(label + '-admitted', ast, parts, helper=helper)
                    changed = [part.copy() for part in parts]; index = parts.index(atoms)
                    changed[index] = list(reversed(atoms))
                    check(label + '-conjunct-order', ast, changed, False, helper)
                    changed[index] = atoms.copy(); changed[index][position] = atom(owner + b'X')
                    check(label + '-self-bytes', ast, changed, False, helper)
                    changed[index][position] = atom(owner.swapcase())
                    check(label + '-self-case', ast, changed, False, helper)
                    changed[index] = atoms[:-1]
                    check(label + '-missing-conjunct', ast, changed, False, helper)
                    changed[index] = atoms + [atom(b'Extra348')]
                    check(label + '-extra-conjunct', ast, changed, False, helper)
                    if helper != INTERSECTION:
                        check(label + '-branch-order', ast, list(reversed(parts)), False, helper)
                rows.append({'id': kind + '-' + str(size) + '-' + str(position) + '-member-context', 'kind': 'members', 'expected': True,
                             'premise': '$hook_short_reference_nominal_intersection_members([' + ','.join(raw) + '],[' + ','.join(atoms) + '],' + lexical + ')'})

        other = names.raw(b'Global348\\I348', 'NNameFullyQualified'); otheratom = atom(b'Global348\\I348')
        group = prior.intersection([other, selfraw]); parts = [[otheratom, atom(owner)]]
        consumer = prior.context(namespace=b'Consumer348', owner=owner, imports=((b'self', b'Wrong348\\Owner'), (b'Box348', b'stdClass')))
        check(kind + '-self-keeps-defining-owner', group, parts, ctx=consumer)
        for scope in ('PTGLOBAL', 'PTDEFERRED', 'PTANONYMOUS true', 'PTANONYMOUS false',
                      'PTTRAIT ' + names.value(b'Def348\\Trait348'), 'PTKNOWN ' + names.value(owner + b'X') + ' eps'):
            check(kind + '-excluded-scope-' + scope, group, parts, False, ctx=prior.context(namespace=b'Def348', owner=owner, scope=scope))
        for label, ctx in (('missing-file', prior.context(namespace=b'Def348', owner=owner, file=b'')),
                           ('missing-line', prior.context(namespace=b'Def348', owner=owner, line=0))):
            check(kind + '-' + label, group, parts, False, ctx=ctx)
        for badkind in ('NIdentifier', 'NNameFullyQualified'):
            check(kind + '-wrong-kind-' + badkind, prior.intersection([other, names.raw(b'self', badkind)]), parts, False)
        for keyword in (b'parent', b'static', b'int', b'iterable', b'_', b'boolean', b'1Bad', b'Bad\x00'):
            check(kind + '-excluded-conjunct-' + keyword.hex(), prior.intersection([other, names.raw(keyword, kind)]), parts, False)
        for duplicate in (selfraw, names.raw(owner, 'NNameFullyQualified'), names.raw(owner.swapcase(), 'NNameFullyQualified')):
            check(kind + '-duplicate-' + str(len(rows)), prior.intersection([selfraw, duplicate]), [[atom(owner), atom(owner)]], False)
        local = prior.intersection([names.raw(b'Local348', 'NNameRelative'), selfraw]); localparts = [[atom(b'Def348\\Local348'), atom(owner)]]
        check(kind + '-ordinary-conjunct-defining-context', local, localparts)
        check(kind + '-consumer-cannot-resolve-ordinary-conjunct', local, localparts, False, ctx=consumer)
        imported = prior.context(namespace=b'Def348', owner=owner, imports=((b'Alias348', b'Payload348\\I348'),))
        check(kind + '-ordinary-conjunct-import', prior.intersection([names.raw(b'aLiAs348'), selfraw]), [[atom(b'Payload348\\I348'), atom(owner)]], ctx=imported)
        check(kind + '-singleton-group', prior.intersection([selfraw]), [[atom(owner)]], False)
        check(kind + '-no-intersection', prior.union([selfraw, other]), [[atom(owner)], [otheratom]], False, NOMINAL)
        check(kind + '-no-builtin', prior.union([group, names.raw(b'Other348', 'NNameFullyQualified')]), parts + [[atom(b'Other348')]], False, MIXED)
        check(kind + '-subsumed-group', prior.union([group, selfraw]), parts + [[atom(owner)]], False, NOMINAL)
        for word in ('object', 'mixed', 'iterable', 'callable', 'void', 'never'):
            check(kind + '-nonquiet-builtin-' + word, prior.union([group, names.raw(word.encode(), 'NIdentifier')]), parts + [['PTBUILTIN "' + word + '"']], False, MIXED)
        for left, right in (('int', 'INT'), ('bool', 'true'), ('true', 'false')):
            check(kind + '-builtin-overlap-' + left + '-' + right, prior.union([group, names.raw(left.encode(), 'NIdentifier'), names.raw(right.encode(), 'NIdentifier')]), parts + [['PTBUILTIN "' + left + '"'], ['PTBUILTIN "' + right.lower() + '"']], False, MIXED)
        second = prior.intersection([selfraw, names.raw(b'Second348', 'NNameFullyQualified')]); secondpart = [atom(owner), atom(b'Second348')]
        check(kind + '-two-scoped-conjunctions', prior.union([group, second]), parts + [secondpart], helper=NOMINAL)
        check(kind + '-two-scoped-conjunctions-mixed', prior.union([group, names.raw(b'array', 'NIdentifier'), second]), parts + [['PTBUILTIN "array"'], secondpart], helper=MIXED)
    check('empty-group', prior.intersection([]), [[]], False)
    rows.append({'id': 'members-empty-base', 'kind': 'members', 'expected': True,
                 'premise': '$hook_short_reference_nominal_intersection_members(eps,eps,' + lexical + ')'})
    rows.append({'id': 'members-length-mismatch', 'kind': 'members', 'expected': False,
                 'premise': '~$hook_short_reference_nominal_intersection_members(eps,[PTCLASS ' + names.value(owner) + '],' + lexical + ')'})

    affected = 0
    for label, module in (('341', prior), ('342', relative), ('343', pair), ('344', flat), ('345', builtin), ('346', mixed), ('347', dnf)):
        for row in module.assertions():
            if ('intersection-hook-admitted' in row['id'] or row['id'].endswith('-intersection-admitted')
                    or row['id'].endswith('-self-intersection-DNF-admitted') or row['id'].endswith('-self-inside-conjunction-admitted')):
                assert row['expected'] is True and not row['premise'].startswith('~')
                rows.append({**row, 'id': 'current-' + label + '-' + row['id'], 'kind': 'affected-current-query'}); affected += 1
    assert affected == 16
    assert len({row['id'] for row in rows}) == len(rows)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    helpers = (prior, relative, pair, flat, builtin, mixed, dnf, prior.names, flat.legacy)
    paths = [Path(__file__), *(Path(module.__file__) for module in helpers), ROOT / 'tests/semantics/error_handler_run.py',
             ROOT / 'spec/semantics/modules.json', ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *modules]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'mode': 'fixture-SL',
              'source_agreement_credit': 0, 'native_observations': 0, 'affected_current_queries': 16, 'passed': False}
    try:
        rows = assertions(); report['premises'] = len(rows); (out / 'assertions.json').write_text(json.dumps(rows, indent=2) + '\n')
        fixture = out / 'protocol.watsup'; fixture.write_text('dec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + row['premise'] + '\n' for row in rows))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(fixture)], out / 'check', 60)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after']
                            and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed'], report.get('stderr', '')[:2000]
    print('pass', report['premises'], 'independent scoped-self intersection assertions, source0')


if __name__ == '__main__':
    main()
