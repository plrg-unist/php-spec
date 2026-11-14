#!/usr/bin/env python3
"""Exact emitted division retains integer values and real Warning histories."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_integer_division_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_integer_operator_special_concat_leading_key_protocol as prior

runner = prior.runner
TWO = ('ADD', prior.ZERO, prior.ZERO, 2)
NEGATIVE_FOUR = ('BITNOT', ('ADD', prior.ZERO, TWO, 3), -4)
TREES = (
    ('DIVIDE', TWO, TWO, 1),
    ('DIVIDE', ('NEGATIVE', prior.ZERO, -1), prior.ZERO, -1),
    ('DIVIDE', prior.INF, prior.ZERO, 0),
    ('DIVIDE', ('MULTIPLY', NEGATIVE_FOUR, TWO, -8), TWO, -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[0] != 'DIVIDE':
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    prior.emitted(checks, tag)
    checks += ['$pfshape(' + expression + ') = PFBINARY DIVIDE ' + expression + '_0 ' + expression + '_1']
    children = []
    for index, child in enumerate(tree[1:3]):
        child_tag = tag + '_' + str(index)
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (porigin_' + child_tag + ')']
        child_value, number = value(checks, child_tag, child)
        checks += ['$coerce_number(' + child_value + ') = COERCED (NINT ' + number + ') false',
                   '$long_range(' + number + ')']
        children.append((child_value, number))
    number = prior.integer(tree[-1])
    result = 'PINT ' + number
    checks += ['$number_binary(DIVIDE, NINT ' + children[0][1] + ', NINT ' + children[1][1] + ') = NUM (NINT ' + number + ')',
               '$long_range(' + number + ')',
               '$binary_apply(S, DIVIDE, ' + children[0][0] + ', ' + children[1][0] + ', 5) = S[.RESULT = KNOWN (' + result + ')]',
               '$string_read_runtime_value(S, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_bytes(S, ' + origin + ') = ($echo_value(' + result + '))']
    return result, number


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
    report['scope'] = 'Four actual emitted DIVIDE roots retain genuine recursive BOOL/PINT children, quiet fitting NINT inputs, pure NUM(NINT i) and exact fitting PINT full-state results/decimal BYTE. Own/both-child source/CODEfalse/read-eps/equal captured precision retain actual REQUEST keys and the existing returning/negative/supplied-throw/bounds owners, cleanup and budgets. Pure numeric-result proof excludes zero divisors, fractional and MIN/-1 FLOAT results even under stale nonnormal RESULT. No FLOAT/compiled-PINT leaf, runtime FLOAT BYTE, compiler/schema/API/owner or387 change; saved natives are reused once and fixture source0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
