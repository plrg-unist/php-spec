#!/usr/bin/env python3
"""Emitted XOR retains sequential quiet truth and real Warning histories."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_xor_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_integer_operator_special_concat_leading_key_protocol as prior

runner = prior.runner
# Only fixture discovery views a resumable checkpoint as NORMAL; its raw state
# remains BUDGET and is checked below before the existing resume projection.
FRONTIER = 'def $retained_frontier(S, 0) = ($string_read_plan(S) =/= eps)'
assert runner.PREFIX.count(FRONTIER) == 1
runner.PREFIX = runner.PREFIX.replace(FRONTIER,
    'def $retained_frontier(S, 0) = ($string_read_plan(S[.COMPLETION = NORMAL]) =/= eps)\n'
    r'  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET')
ONE = ('POSITIVE', prior.ZERO, 1)
INTEGER_ZERO = ('POSITIVE', prior.INF, 0)
TWO = ('ADD', prior.ZERO, prior.ZERO, 2)
TREES = (
    ('LOGICALXOR', prior.ZERO, prior.INF, True, False, True),
    ('NEGATIVE', ('LOGICALXOR', ('FLOAT', 0), ONE, False, True, True), -1),
    ('POSITIVE', ('LOGICALXOR', prior.ZERO, TWO, True, True, False), 0),
    ('BITNOT', ('ADD', ('LOGICALXOR', ('FLOAT', 9218868437227405312), INTEGER_ZERO, True, False, True),
               ('ADD', ('LOGICALXOR', ONE, prior.INF, True, False, True),
                ('LOGICALXOR', prior.INF, prior.ZERO, False, True, True), 2), 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[0] != 'LOGICALXOR':
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    prior.emitted(checks, tag)
    checks += ['$pfshape(' + expression + ') = PFBINARY LOGICALXOR ' + expression + '_0 ' + expression + '_1']
    children = []
    for index, child in enumerate(tree[1:3]):
        child_tag = tag + '_' + str(index)
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (porigin_' + child_tag + ')']
        children.append(value(checks, child_tag, child)[0])
    left, right, result = ('PBOOL ' + str(bit).lower() for bit in tree[3:])
    checks += ['S.COMPLETION = NORMAL',
               '$truth(S, ' + children[0] + ') = ' + str(tree[3]).lower(),
               '$truth(S, ' + children[1] + ') = ' + str(tree[4]).lower(),
               '$truth_value(S, ' + children[0] + ', 5) = S[.RESULT = KNOWN (' + left + ')]',
               '$truth_value(S[.RESULT = KNOWN (' + left + ')], ' + children[1] + ', 5) = S[.RESULT = KNOWN (' + right + ')]',
               '$binary_apply(S, LOGICALXOR, ' + children[0] + ', ' + children[1] + ', 5) = S[.RESULT = KNOWN (' + result + ')]',
               '$string_read_runtime_value(S, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_bytes(S, ' + origin + ') = ($echo_value(' + result + '))']
    return result, '1' if tree[-1] else '0'


prior.value, prior.TREES = value, TREES
authority = prior.authority


def conditions(program, path, index):
    checks, derived = prior.conditions(program, path, index)
    at = checks.index(r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET')
    checks[at:at + 1] = ['S_found.COMPLETION = BUDGET', '$string_read_plan(S_found) = eps']
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
    report['scope'] = 'Four actual emitted LOGICALXOR trees retain recursively typed quiet PFLOAT/PBOOL/PINT children, pure truth bits, sequential full-state quiet truth conversions and exact unchanged binary_apply. Runtime certification explicitly requires NORMAL without normalizing state. Fixture frontier discovery alone probes a guarded NORMAL view of normal/budget checkpoints; the actual selected BUDGET state refuses string_read_plan before the existing resume projection. Actual own/both-child source/CODEfalse/read-eps/equal captured precision preserve genuine Boolean results under signs/ADD/BITNOT and existing REQUEST keys, returning/negative/supplied-throw/bounds owners, cleanup and zero/one-step budget rejoining. BOOLtrue xor PINT2 is false through truth conversion. No new leaves, NaN truth, runtime FLOAT producer/BYTE, short-circuit/compiler/schema/API/51/387/kernel/owner expansion; saved natives are reused once and fixture source0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
