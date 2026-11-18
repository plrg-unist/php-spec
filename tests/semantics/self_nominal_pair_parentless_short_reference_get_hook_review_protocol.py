#!/usr/bin/env python3
"""Independent scoped-self pair order, context and boundary counterexamples."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import self_parentless_short_reference_get_hook_review_protocol as prior
import relative_self_parentless_short_reference_get_hook_review_protocol as relative
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
HELPER = '$hook_short_reference_nominal_pair_header'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def assertions():
    rows = []; names = prior.names; owner = b'Def343\\Box343'
    lexical = prior.context(namespace=b'Def343', owner=owner, file=b'original343.php')

    def check(label, ast, normalized, ctx=lexical, expected=True, helper=HELPER):
        rows.append({'id': label, 'expected': expected, 'premise': ('' if expected else '~') +
                     helper + '(' + ast + ',' + normalized + ',' + ctx + ')'})

    def pair(*members):
        return prior.union(list(members))

    def mask(*classes):
        return prior.branches([['PTCLASS ' + names.value(name)] for name in classes])

    imported = prior.context(namespace=b'Def343', owner=owner, file=b'original343.php',
                             imports=((b'Alias343', b'Payload343\\Other'), (b'self', b'Foreign343\\Wrong')))
    choices = [('local', b'Other', 'NName', b'Def343\\Other', lexical),
               ('relative', b'Other', 'NNameRelative', b'Def343\\Other', lexical),
               ('fully-qualified', b'Payload343\\Other', 'NNameFullyQualified', b'Payload343\\Other', lexical),
               ('imported', b'aLiAs343', 'NName', b'Payload343\\Other', imported)]
    for kind in ('NName', 'NNameRelative'):
        for label, text, other_kind, target, ctx in choices:
            raw_self = names.raw(b'SeLf', kind); other = names.raw(text, other_kind)
            for reverse in (False, True):
                raw = [raw_self, other]; resolved = [owner, target]
                if reverse: raw.reverse(); resolved.reverse()
                label_full = kind + '-' + label + '-' + str(reverse)
                ast = pair(*raw); normalized = mask(*resolved)
                check(label_full, ast, normalized, ctx)
                check(label_full + '-raw-order', pair(*reversed(raw)), normalized, ctx, False)
                check(label_full + '-normalized-order', ast, mask(*reversed(resolved)), ctx, False)
                for position in (0, 1):
                    altered = resolved.copy(); altered[position] += b'X'
                    check(label_full + '-bytes-' + str(position), ast, mask(*altered), ctx, False)
                    altered = resolved.copy(); altered[position] = altered[position].swapcase()
                    check(label_full + '-case-' + str(position), ast, mask(*altered), ctx, False)
                check(label_full + '-not-many-builtins', ast, normalized, ctx, False,
                      '$hook_short_reference_class_builtin_union_header')

        raw_self = names.raw(b'self', kind); other = names.raw(b'Other', 'NNameFullyQualified')
        ast = pair(raw_self, other); normalized = mask(owner, b'Other')
        for scope in ('PTGLOBAL', 'PTDEFERRED', 'PTANONYMOUS true', 'PTANONYMOUS false',
                      'PTTRAIT ' + names.value(b'Def343\\Trait'),
                      'PTKNOWN ' + names.value(b'Foreign343\\Box343') + ' eps'):
            check(kind + '-scope-' + scope, ast, normalized,
                  prior.context(namespace=b'Def343', owner=owner, scope=scope), False)
        for label, ctx in [('missing-file', prior.context(namespace=b'Def343', owner=owner, file=b'')),
                           ('missing-line', prior.context(namespace=b'Def343', owner=owner, line=0))]:
            check(kind + '-' + label, ast, normalized, ctx, False)
        consumer = prior.context(namespace=b'Consumer343', owner=owner,
                                 imports=((b'self', b'Foreign343\\Wrong'), (b'Other', b'stdClass')))
        check(kind + '-scope-survives-consumer-and-fake-self-import', ast, normalized, consumer)
        check(kind + '-ordinary-other-cannot-use-consumer-context',
              pair(raw_self, names.raw(b'Other')), mask(owner, b'Def343\\Other'), consumer, False)
        check(kind + '-duplicate-self', pair(raw_self, raw_self), mask(owner, owner), expected=False)
        check(kind + '-duplicate-owner-name', pair(raw_self, names.raw(owner, 'NNameFullyQualified')),
              mask(owner, owner), expected=False)
        for bad in (b'', b'_', b'parent', b'static', b'int', b'callable', b'Nested\\INT',
                    b'1Other', b'Other\x00', b'Other-Name', b'boolean', b'resource'):
            check(kind + '-bad-other-' + bad.hex(), pair(raw_self, names.raw(bad)),
                  mask(owner, b'Def343\\' + bad), expected=False)
        for bad_kind in ('NIdentifier', 'NNameFullyQualified'):
            check(kind + '-bad-self-kind-' + bad_kind, pair(names.raw(b'self', bad_kind), other),
                  normalized, expected=False)
        for label, raw, typed in [
            ('single', pair(raw_self), mask(owner)),
            ('three', pair(raw_self, other, names.raw(b'Third')), mask(owner, b'Other', b'Def343\\Third')),
            ('intersection', prior.intersection([raw_self, other]),
             prior.branches([['PTCLASS ' + names.value(owner), 'PTCLASS ' + names.value(b'Other')]])),
            ('nullable-self', names.raw(b'self', kind, True), names.mask(owner, True)),
        ]:
            check(kind + '-shape-' + label, raw, typed, expected=False)
        for label, typed in [('empty', 'eps'), ('missing', mask(owner)),
                             ('extra', mask(owner, b'Other', b'Third')),
                             ('scope', prior.branches([['PTSELF'], ['PTCLASS ' + names.value(b'Other')]])),
                             ('builtin', prior.branches([['PTCLASS ' + names.value(owner)], ['PTBUILTIN "object"']]))]:
            check(kind + '-normalized-' + label, ast, typed, expected=False)
        three = pair(raw_self, other, names.raw(b'Third'))
        check(kind + '-larger-fold-unchanged', three, mask(owner, b'Other', b'Def343\\Third'), expected=False,
              helper='$hook_short_reference_nominal_union_header')
        inter = prior.intersection([raw_self, other])
        inter_type = prior.branches([['PTCLASS ' + names.value(owner), 'PTCLASS ' + names.value(b'Other')]])
        check(kind + '-intersection-unchanged', inter, inter_type, expected=False,
              helper='$hook_short_reference_nominal_intersection_header')
        grouped = prior.intersection([other, names.raw(b'Third')])
        dnf_type = prior.branches([['PTCLASS ' + names.value(b'Other'), 'PTCLASS ' + names.value(b'Def343\\Third')],
                                   ['PTCLASS ' + names.value(owner)]])
        check(kind + '-dnf-unchanged', pair(grouped, raw_self), dnf_type, expected=False,
              helper='$hook_short_reference_nominal_dnf_header')

    # These are the only two existing header assertions whose outcomes change.
    for label, module in [('old341', prior), ('old342-inherited', relative)]:
        original = next(row for row in module.assertions() if row['id'] == 'self-ordinary-pair-accepted')
        rows.append({'id': 'promoted-' + label + '-self-ordinary-pair', 'expected': True,
                     'premise': original['premise'].removeprefix('~')})
    assert len({row['id'] for row in rows}) == len(rows)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(prior.__file__), Path(relative.__file__), Path(prior.names.__file__),
             ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'spec/semantics/modules.json',
             ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *modules]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'mode': 'fixture-SL',
              'source_agreement_credit': 0, 'native_observations': 0, 'promoted_old_queries': 2, 'passed': False}
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
    print('pass', report['premises'], 'independent scoped-self pair assertions, source0')


if __name__ == '__main__':
    main()
