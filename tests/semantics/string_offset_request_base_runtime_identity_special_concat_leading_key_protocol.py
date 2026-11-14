#!/usr/bin/env python3
"""Emitted strict identity retains typed values and real Warning histories."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_identity_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_integer_operator_special_concat_leading_key_protocol as prior

runner = prior.runner
DIFFERENT_TYPES = ('NOTIDENTICAL', prior.ZERO, ('POSITIVE', prior.ZERO, 1), True)
SAME_INTEGERS = ('IDENTICAL', ('POSITIVE', prior.ZERO, 1), ('POSITIVE', prior.ZERO, 1), True)
FLOAT_INTEGER = ('IDENTICAL', ('FLOAT', 0), ('POSITIVE', prior.INF, 0), False)
TREES = (
    DIFFERENT_TYPES,
    ('NEGATIVE', SAME_INTEGERS, -1),
    ('POSITIVE', FLOAT_INTEGER, 0),
    ('BITNOT', ('ADD', DIFFERENT_TYPES,
               ('ADD', ('NOTIDENTICAL', ('POSITIVE', prior.INF, 0), ('FLOAT', 0), True),
                ('IDENTICAL', prior.ZERO, prior.ZERO, True), 2), 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    kind = tree[0]
    if kind not in ('IDENTICAL', 'NOTIDENTICAL'):
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
    result = 'PBOOL ' + str(tree[-1]).lower()
    identical = tree[-1] if kind == 'IDENTICAL' else not tree[-1]
    checks += ['$strict_identical(' + children[0] + ', ' + children[1] + ') = ' + str(identical).lower(),
               '$strict_check(S, ' + children[0] + ', ' + children[1] + ', eps) = COMPARED ' + str(identical).lower(),
               '$binary_apply(S, ' + kind + ', ' + children[0] + ', ' + children[1] + ', 5) = S[.RESULT = KNOWN (' + result + ')]',
               '$string_read_runtime_value(S, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_bytes(S, ' + origin + ') = ($echo_value(' + result + '))']
    return result, '1' if tree[-1] else '0'


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
    report['scope'] = 'Four actual emitted IDENTICAL/NOTIDENTICAL trees retain recursively typed quiet PFLOAT/PBOOL/PINT children, exact pure strict-identical Boolean and unchanged whole-state binary_apply. Own/both-child source/CODEfalse/read-eps/equal captured precision retain actual REQUEST keys and returning/negative/supplied-throw/bounds owners, cleanup and budgets. BOOLtrue/PINT1 and PFLOAT0/PINT0 remain nonidentical; existing signs/ADD/BITNOT consume genuine Boolean results. No NULL/string/array/object leaf, NaN truth/BYTE, runtime FLOAT producer/formatting, compiler/schema/API/387/kernel/owner expansion; saved natives are reused once and fixture source0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
