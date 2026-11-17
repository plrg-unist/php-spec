#!/usr/bin/env python3
"""Weak NaN equality retains typed results and comparison-specific dispatch."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_nan_equality_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_nan_identity_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
NANS, TRUTH = prior.NANS, ('NOT', ('FLOAT', 0), True)
TREES = (
    ('POSITIVE', ('EQUAL', NANS[0], TRUTH, 0, True), 1),
    ('BITNOT', ('CAST', 'CASTINT', ('EQUAL', ('FLOAT', 4607182418800017408), NANS[1], 1, False), 'PINT 0'), -1),
    ('CAST', 'CASTINT', ('EQUAL', NANS[2], ('LITERAL_INT', 0), 1, False), 'PINT 0'),
    ('BITNOT', ('ADD', ('CAST', 'CASTINT', ('NOTEQUAL', NANS[3], ('NAN', 'CONSTANT'), 1, True), 'PINT 1'),
               ('COMPILED', 'PINT 2', ('ADD', 1, 1)), 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[0] not in ('EQUAL', 'NOTEQUAL'):
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
    result, order = 'PBOOL ' + str(tree[-1]).lower(), str(tree[-2])
    checks += ['$scalar_order(S, ' + children[0] + ', ' + children[1] + ') = ' + order,
               '$comparison_value(' + tree[0] + ', ' + order + ') = ' + result,
               '$binary_apply(S, ' + tree[0] + ', ' + children[0] + ', ' + children[1] + ', 5) = S[.RESULT = KNOWN (' + result + ')]',
               '$string_read_runtime_value(S, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_bytes(S, ' + origin + ') = ($echo_value(' + result + '))']
    return result, '1' if tree[-1] else '0'


module = prior
while module is not integers:
    module.value = value
    module = module.prior
integers.value, integers.TREES = value, TREES


def conditions(program, path, index):
    checks, derived = prior.conditions(program, path, index)
    if index == 3:
        checks += ['$string_read_runtime_value(S, porigin_operator_0_0_0) = (PBOOL true)']
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
    report['scope'] = 'Three source-reached histories and one targeted compiled-state root fixture admit weak EQUAL/NOTEQUAL with at least one exact recursive NaN under NORMAL, own/both-child source, CODEfalse/read-eps/positive line and equal captured precision. Comparison-specific scalar_order/comparison_value and unchanged whole binary_apply retain NaN==true, numeric non-equality and NaN!=NaN without generic NaN truth conversion. Proper existing Boolean/integer parents preserve keys1/-1/0/-4. Fourth uses checked original Program/php_run0 at actual key origin with initial live/captured14 and S_after=S, proving NOTEQUAL=true, PINT-4 and BYTE-4x without callback/ownership/bounds/resumption credit. Those remain original-source comparisons; first three full histories keep captured14/live17. Legacy equality/BUDGET, general NaN VALUE/BYTE/truth, compiler/numerics, owners/lifetimes and all holds remain literal. Native originals reused once; fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
