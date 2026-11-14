#!/usr/bin/env python3
"""Emitted ordering retains scalar direction and real Warning histories."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_order_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_integer_operator_special_concat_leading_key_protocol as prior

runner = prior.runner
ONE = ('POSITIVE', prior.ZERO, 1)
INTEGER_ZERO = ('POSITIVE', prior.INF, 0)
TWO = ('ADD', prior.ZERO, prior.ZERO, 2)
TREES = (
    ('LESSEQUAL', prior.ZERO, TWO, 0, 0, True),
    ('NEGATIVE', ('LESS', ('FLOAT', 0), ONE, -1, 1, True), -1),
    ('POSITIVE', ('GREATER', ('NEGATIVE', ONE, -1), ('FLOAT', 0), -1, 1, False), 0),
    ('BITNOT', ('ADD', ('GREATEREQUAL', ONE, ('FLOAT', 0), 1, -1, True),
               ('ADD', ('SPACESHIP', prior.ZERO, prior.INF, 1, -1, 1),
                ('SPACESHIP', ONE, INTEGER_ZERO, 1, -1, 1), 2), 3), -4),
)
OPERATORS = ('LESS', 'LESSEQUAL', 'GREATER', 'GREATEREQUAL', 'SPACESHIP')
base_value = prior.value


def value(checks, tag, tree):
    kind = tree[0]
    if kind not in OPERATORS:
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    prior.emitted(checks, tag)
    checks += ['$pfshape(' + expression + ') = PFBINARY ' + kind + ' ' + expression + '_0 ' + expression + '_1']
    children = []
    for index, child in enumerate(tree[1:3]):
        child_tag = tag + '_' + str(index)
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (porigin_' + child_tag + ')']
        children.append(value(checks, child_tag, child)[0])
    forward, reverse = map(prior.integer, tree[3:5])
    number = prior.integer(tree[-1]) if kind == 'SPACESHIP' else '1' if tree[-1] else '0'
    result = 'PINT ' + number if kind == 'SPACESHIP' else 'PBOOL ' + str(tree[-1]).lower()
    order = reverse if kind in ('GREATER', 'GREATEREQUAL') else forward
    checks += ['$scalar_order(S, ' + children[0] + ', ' + children[1] + ') = ' + forward,
               '$scalar_order(S, ' + children[1] + ', ' + children[0] + ') = ' + reverse,
               '$comparison_value(' + kind + ', ' + order + ') = ' + result,
               '$binary_apply(S, ' + kind + ', ' + children[0] + ', ' + children[1] + ', 5) = S[.RESULT = KNOWN (' + result + ')]',
               '$string_read_runtime_value(S, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_bytes(S, ' + origin + ') = ($echo_value(' + result + '))']
    if kind == 'SPACESHIP':
        checks += ['$long_range(' + number + ')']
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
    report['scope'] = 'Four actual emitted LESS/LESSEQUAL/GREATER/GREATEREQUAL/SPACESHIP trees retain recursively typed quiet PFLOAT/PBOOL/PINT children, both pure scalar_order directions, direction-selected comparison_value and unchanged whole-state binary_apply. Exact own/both-child source/CODEfalse/read-eps/equal captured precision preserve genuine Boolean and fitting integer results under signs/ADD/BITNOT and existing REQUEST keys, returning/negative/supplied-throw/bounds owners, cleanup and zero/one-step rejoining. Greater forms explicitly use reversed scalar_order; Boolean truth order and numeric order remain distinct. No new leaves, NaN, runtime FLOAT producers/BYTE, compiler/schema/API/387/kernel/owner expansion; saved natives are reused once and fixture source0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
