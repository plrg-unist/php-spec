#!/usr/bin/env python3
"""Independent scoped-self class/builtin union order and boundary controls."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import self_parentless_short_reference_get_hook_review_protocol as prior
import relative_self_parentless_short_reference_get_hook_review_protocol as relative
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
HELPER = '$hook_short_reference_class_builtin_union_header'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def assertions():
    rows = []; names = prior.names; owner = b'Def345\\Box345'
    lexical = prior.context(namespace=b'Def345', owner=owner, file=b'original345.php')
    atom = 'PTCLASS ' + names.value(owner)

    def check(label, raw, typed, context=lexical, expected=True, helper=HELPER):
        rows.append({'id': label, 'expected': expected, 'premise': ('' if expected else '~') +
                     helper + '(' + raw + ',' + typed + ',' + context + ')'})

    def forms(kind, builtins, position):
        raw = [names.raw(text.encode(), 'NIdentifier') for text in builtins]
        typed = [['PTBUILTIN "' + text.lower() + '"'] for text in builtins]
        raw.insert(position, names.raw(b'SeLf', kind)); typed.insert(position, [atom])
        return raw, typed

    for kind in ('NName', 'NNameRelative'):
        for builtins in (['int', 'null'], ['float', 'bool', 'string'],
                         ['array', 'string', 'int', 'float', 'null', 'false']):
            for position in sorted({0, len(builtins) // 2, len(builtins)}):
                raw, typed = forms(kind, builtins, position)
                ast = prior.union(raw); mask = prior.branches(typed)
                label = kind + '-' + str(len(raw)) + '-' + str(position)
                check(label, ast, mask)
                check(label + '-raw-order', prior.union(list(reversed(raw))), mask, expected=False)
                check(label + '-normalized-order', ast, prior.branches(list(reversed(typed))), expected=False)
                altered = [part.copy() for part in typed]; altered[position] = ['PTCLASS ' + names.value(owner + b'X')]
                check(label + '-self-bytes', ast, prior.branches(altered), expected=False)
                altered[position] = ['PTCLASS ' + names.value(owner.swapcase())]
                check(label + '-self-case', ast, prior.branches(altered), expected=False)
                check(label + '-missing', ast, prior.branches(typed[:-1]), expected=False)
                check(label + '-extra', ast, prior.branches(typed + [['PTBUILTIN "true"']]), expected=False)
                upper = raw.copy()
                for index in range(len(upper)):
                    if index != position:
                        text = builtins[index if index < position else index - 1]
                        upper[index] = names.raw(text.upper().encode(), 'NIdentifier')
                check(label + '-uppercase-builtins', prior.union(upper), mask)

        raw, typed = forms(kind, ['int', 'null'], 1)
        ast = prior.union(raw); mask = prior.branches(typed)
        consumer = prior.context(namespace=b'Consumer345', owner=owner,
                                 imports=((b'self', b'Foreign345\\Wrong'), (b'Box345', b'stdClass')))
        check(kind + '-known-self-survives-consumer-and-fake-imports', ast, mask, consumer)
        for scope in ('PTGLOBAL', 'PTDEFERRED', 'PTANONYMOUS true', 'PTANONYMOUS false',
                      'PTTRAIT ' + names.value(b'Def345\\Trait345'),
                      'PTKNOWN ' + names.value(b'Wrong345\\Box345') + ' eps'):
            check(kind + '-scope-' + scope, ast, mask,
                  prior.context(namespace=b'Def345', owner=owner, scope=scope), False)
        check(kind + '-missing-file', ast, mask, prior.context(namespace=b'Def345', owner=owner, file=b''), False)
        check(kind + '-missing-line', ast, mask, prior.context(namespace=b'Def345', owner=owner, line=0), False)
        for wrong_kind in ('NIdentifier', 'NNameFullyQualified'):
            altered = raw.copy(); altered[1] = names.raw(b'self', wrong_kind)
            check(kind + '-wrong-self-kind-' + wrong_kind, prior.union(altered), mask, expected=False)
        parent_scope = 'PTKNOWN ' + names.value(owner) + ' (' + names.value(b'Def345\\Parent345') + ')'
        parent_context = prior.context(namespace=b'Def345', owner=owner, scope=parent_scope)
        parent_raw = raw.copy(); parent_raw[1] = names.raw(b'parent', kind)
        parent_typed = [part.copy() for part in typed]; parent_typed[1] = ['PTCLASS ' + names.value(b'Def345\\Parent345')]
        parent_ast = prior.union(parent_raw); parent_mask = prior.branches(parent_typed)
        rows.append({'id': kind + '-known-parent-normalizes', 'expected': True,
                     'premise': '$ptype_normalize(' + parent_ast + ',' + parent_context + ') = PTOK (' + parent_mask + ') eps'})
        check(kind + '-known-parent-stays-excluded', parent_ast, parent_mask, parent_context, False)

        for parts in (['int', 'int'], ['INT', 'int'], ['bool', 'true'], ['bool', 'false'], ['true', 'false']):
            bad_raw, bad_typed = forms(kind, parts, 0)
            check(kind + '-duplicate-or-overlap-' + '-'.join(parts), prior.union(bad_raw), prior.branches(bad_typed), expected=False)
        for builtin in ('object', 'mixed', 'callable', 'iterable', 'void', 'never', 'integer', 'resource'):
            bad_raw, bad_typed = forms(kind, ['int', builtin], 1)
            check(kind + '-excluded-builtin-' + builtin, prior.union(bad_raw), prior.branches(bad_typed), expected=False)
        for wrong_kind in ('NName', 'NNameFullyQualified', 'NNameRelative'):
            altered = raw.copy(); altered[0] = names.raw(b'int', wrong_kind)
            check(kind + '-builtin-raw-kind-' + wrong_kind, prior.union(altered), mask, expected=False)
        for count in (0, 1):
            short_raw, short_typed = forms(kind, ['int'][:count], 0)
            check(kind + '-too-short-' + str(len(short_raw)), prior.union(short_raw), prior.branches(short_typed), expected=False)
        long_raw, long_typed = forms(kind, ['array', 'string', 'int', 'float', 'null', 'false', 'int'], 3)
        check(kind + '-too-long', prior.union(long_raw), prior.branches(long_typed), expected=False)
        check(kind + '-not-union', raw[1], mask, expected=False)
        check(kind + '-nullable', names.raw(b'self', kind, True), mask, expected=False)
        second = names.raw(b'Other', 'NNameFullyQualified')
        two_classes = prior.union([raw[1], second, names.raw(b'int', 'NIdentifier')])
        two_typed = prior.branches([[atom], ['PTCLASS ' + names.value(b'Other')], ['PTBUILTIN "int"']])
        check(kind + '-second-class-excluded', two_classes, two_typed, expected=False)
        check(kind + '-mixed-fold-unchanged', two_classes, two_typed, expected=True,
              helper='$hook_short_reference_mixed_nominal_union_header')
        inter = prior.intersection([raw[1], second])
        inter_typed = prior.branches([[atom, 'PTCLASS ' + names.value(b'Other')]])
        check(kind + '-intersection-admitted', inter, inter_typed, expected=True,
              helper='$hook_short_reference_nominal_intersection_header')
        group = prior.intersection([second, names.raw(b'Third', 'NNameFullyQualified')])
        dnf_typed = prior.branches([['PTCLASS ' + names.value(b'Other'), 'PTCLASS ' + names.value(b'Third')], [atom]])
        check(kind + '-DNF-unchanged', prior.union([group, raw[1]]), dnf_typed, expected=True,
              helper='$hook_short_reference_nominal_dnf_header')
        mixed_dnf_typed = prior.branches([['PTCLASS ' + names.value(b'Other'), 'PTCLASS ' + names.value(b'Third')],
                                          [atom], ['PTBUILTIN "int"']])
        check(kind + '-mixed-DNF-unchanged', prior.union([group, raw[1], names.raw(b'int', 'NIdentifier')]), mixed_dnf_typed,
              expected=True, helper='$hook_short_reference_mixed_nominal_dnf_header')
        nominal = prior.union([raw[1], second, names.raw(b'Third', 'NNameFullyQualified')])
        nominal_typed = prior.branches([[atom], ['PTCLASS ' + names.value(b'Other')], ['PTCLASS ' + names.value(b'Third')]])
        check(kind + '-accepted-nominal-fold-retained', nominal, nominal_typed,
              helper='$hook_short_reference_nominal_union_header')

    for label, module in [('old341', prior), ('old342-inherited', relative)]:
        original = next(row for row in module.assertions() if row['id'] == 'three-arm-builtin-self-accepted')
        rows.append({**original, 'id': 'promoted-' + label + '-three-arm-builtin-self'})
    for needed in (False, True):
        rows.append({'id': 'member-empty-needs-class-' + str(needed), 'expected': not needed,
                     'premise': ('' if not needed else '~') + '$hook_short_reference_class_builtin_union_members(eps,eps,' +
                                str(needed).lower() + ',' + lexical + ')'})
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
    print('pass', report['premises'], 'independent scoped-self multi-builtin assertions, source0')


if __name__ == '__main__':
    main()
