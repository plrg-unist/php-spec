#!/usr/bin/env python3
"""Strict-PINT integer trees retain actual temporary and Warning authority."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_integer_binary_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_integer_operator_special_concat_leading_key_protocol as prior

runner = prior.runner
INTEGER_OPS = ('MODULO', 'BITAND', 'BITOR', 'BITXOR', 'SHIFTLEFT', 'SHIFTRIGHT')
ONE, ZERO = ('POSITIVE', prior.ZERO, 1), ('POSITIVE', prior.INF, 0)
TWO = ('POSITIVE', ('ADD', prior.ZERO, prior.ZERO, 2), 2)
THREE = ('ADD', prior.ZERO, ('ADD', prior.ZERO, prior.ZERO, 2), 3)
NEGATIVE_FOUR = ('POSITIVE', ('BITNOT', THREE, -4), -4)
TREES = (
    ('BITAND', ('POSITIVE', ('MODULO', ONE, TWO, 1), 1), ONE, 1),
    ('BITOR', ('POSITIVE', ('BITNOT', ZERO, -1), -1), ZERO, -1),
    ('BITXOR', ONE, ONE, 0),
    ('SHIFTRIGHT', ('POSITIVE', ('SHIFTLEFT', NEGATIVE_FOUR, ONE, -8), -8), ONE, -4),
)
base_value = prior.value


def value(checks, tag, tree):
    kind = tree[0]
    if kind not in INTEGER_OPS:
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    prior.emitted(checks, tag)
    checks += ['$pfshape(' + expression + ') = PFBINARY ' + kind + ' ' + expression + '_0 ' + expression + '_1']
    children = []
    for index, child in enumerate(tree[1:3]):
        child_tag = tag + '_' + str(index)
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (porigin_' + child_tag + ')']
        child_value, number = value(checks, child_tag, child)
        assert child_value.startswith('PINT ')
        checks += ['$integer_tmp_source(expression_' + child_tag + ')', '$long_range(' + number + ')']
        children.append((child_value, number))
    number = prior.integer(tree[-1])
    result = 'PINT ' + number
    checks += ['$integer_binary(' + kind + ', ' + children[0][1] + ', ' + children[1][1] + ') = IRESULT ' + number,
               '$long_range(' + number + ')',
               '$binary_apply(S, ' + kind + ', ' + children[0][0] + ', ' + children[1][0] + ', 5) = S[.RESULT = KNOWN (' + result + ')]',
               '$string_read_runtime_value(S, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_bytes(S, ' + origin + ') = ($echo_value(' + result + '))']
    return result, number


# Reuse the unchanged source/owner/history fixture with the new exact trees.
prior.value, prior.TREES = value, TREES
authority, conditions = prior.authority, prior.conditions


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
    report['scope'] = 'Four source-reached MOD/AND/OR/XOR/SL/SR trees retain strict typed PINT children, genuine unary+ TMP operands under unchanged387, exact own/both-child source/CODEfalse/read-eps/equal captured precision, fitting inputs and exact IRESULT/full-state PINT results/decimal bytes. No BOOL/FLOAT/compiled-PINT leaf, error kernel, formatter, compiler/API/owner expansion is introduced. Actual REQUEST keys preserve the same returning/negative/supplied-throw/bounds owners, cleanup and budgets. Saved natives are reused once; fixture source0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
