#!/usr/bin/env python3
"""Ordered NaN comparisons retain unordered results and reversed operands."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_nan_ordered_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_nan_equality_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
NANS = prior.NANS
TREES = (
    ('POSITIVE', ('IDENTICAL', ('SPACESHIP', NANS[0], ('NAN', 'CONSTANT'), 1, 'PINT 1'), ('LITERAL_INT', 1), True), 1),
    ('BITNOT', ('CAST', 'CASTINT', ('LESS', ('FLOAT', 4607182418800017408), NANS[1], 1, 'PBOOL false'), 'PINT 0'), -1),
    ('CAST', 'CASTINT', ('GREATER', NANS[2], ('LITERAL_INT', 0), 1, 'PBOOL false'), 'PINT 0'),
    ('BITNOT', ('ADD', ('CAST', 'CASTINT', ('GREATEREQUAL',
               ('LESSEQUAL', NANS[3], ('NAN', 'CONSTANT'), 1, 'PBOOL false'), ('NAN', 'CONSTANT'), 1, 'PBOOL false'), 'PINT 0'),
               ('COMPILED', 'PINT 3', ('ADD', 1, 2)), 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[0] not in ('LESS', 'LESSEQUAL', 'GREATER', 'GREATEREQUAL', 'SPACESHIP'):
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    integers.emitted(checks, tag)
    checks += ['$pfshape(' + expression + ') = PFBINARY ' + tree[0] + ' ' + expression + '_0 ' + expression + '_1']
    children = []
    for index, child in enumerate(tree[1:3]):
        child_origin = 'porigin_' + tag + '_' + str(index)
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (' + child_origin + ')',
                   '$origin_node(S.SOURCES, ' + child_origin + ') = (' + expression + '_' + str(index) + ')',
                   '$compiled_precision(S, (' + child_origin + ')) = (14)']
        children.append(value(checks, tag + '_' + str(index), child)[0])
    checks += ['S.COMPLETION = NORMAL',
               '$string_read_runtime_instanceof_operand(S, porigin_' + tag + '_0) = (' + children[0] + ')',
               '$string_read_runtime_instanceof_operand(S, porigin_' + tag + '_1) = (' + children[1] + ')',
               '$pfcast_nan(' + children[0] + r') \/ $pfcast_nan(' + children[1] + ')']
    result, order = tree[-1], str(tree[-2])
    ordered = children[::-1] if tree[0] in ('GREATER', 'GREATEREQUAL') else children
    checks += ['$scalar_order(S, ' + ordered[0] + ', ' + ordered[1] + ') = ' + order,
               '$long_range(' + order + ')',
               '$comparison_value(' + tree[0] + ', ' + order + ') = ' + result,
               '$binary_apply(S, ' + tree[0] + ', ' + children[0] + ', ' + children[1] + ', 5) = S[.RESULT = KNOWN (' + result + ')]',
               '$string_read_runtime_value(S, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_bytes(S, ' + origin + ') = ($echo_value(' + result + '))']
    if tree[0] == 'SPACESHIP':
        checks += ['$strict_identical(' + result + ', PBOOL true) = false']
    return result, result.removeprefix('PINT ') if result.startswith('PINT ') else '1' if result == 'PBOOL true' else '0'


module = prior
while module is not integers:
    module.value = value
    module = module.prior
integers.value, integers.TREES = value, TREES


def conditions(program, path, index):
    checks, derived = prior.conditions(program, path, index)
    if index == 3:
        old = '$string_read_runtime_value(S, porigin_operator_0_0_0) = (PBOOL true)'
        assert checks.count(old) == 1
        checks[checks.index(old)] = old.replace('true', 'false')
        checks += ['$string_read_runtime_value(S, porigin_operator_0_0_0_0) = (PBOOL false)']
    return checks, derived


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = {Path(module.__file__).resolve() for module in tuple(sys.modules.values())
               if getattr(module, '__file__', None)
               and Path(module.__file__).resolve().parent == Path(__file__).resolve().parent}
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.OUTPUTS, runner.conditions = cases, tuple(cases.OUTPUTS.values()), conditions
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Three source-reached histories and one targeted compiled-state root fixture authenticate LESS/LESSEQUAL/GREATER/GREATEREQUAL/SPACESHIP with at least one genuine recursive NaN under NORMAL, own/both-source CODEfalse/read-eps/positive-line and equal captured precision. Pure scalar_order/comparison_value and unchanged whole binary_apply retain Boolean results and fitting PINT spaceship. Greater comparisons use actual reversed operands, not negated source order. Existing scalar NaN compatibility remains comparison-specific without general NaN truth or formatting. Typed parents retain keys1/-1/0/-4; fourth uses actual checked Program/php_run0 compiled root with initial14/S_after=S and no callback/owner/bounds/resumption renewal. Native originals reused once, source0/native0 fixtures. Old ordered/BUDGET arms, compiler/numerics, generic NaN VALUE/BYTE/truth, owners/lifetimes and all exact holds remain literal.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
