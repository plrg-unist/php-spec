#!/usr/bin/env python3
"""Quiet POWERDONE integer values retain exact typed operands and key owners."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_integer_power_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_float_bitnot_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
ONE, THREE, TRUE, NULL = prior.prior.prior.ONE, prior.prior.prior.THREE, prior.prior.prior.TRUE, prior.prior.prior.NULL
ZERO = ('POSITIVE', ('NOT', ('FLOAT', 9218868437227405312), False), 0)
TREES = (
    ('POSITIVE', ('POWER', ONE, THREE, 1), 1),
    ('BITNOT', ('POWER', ZERO, ONE, 0), -1),
    ('POSITIVE', ('POWER', NULL, TRUE, 0), 0),
    ('BITNOT', ('POWER', THREE, ONE, 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[0] != 'POWER':
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    integers.emitted(checks, tag)
    checks += ['$pfshape(' + expression + ') = PFBINARY POWER ' + expression + '_0 ' + expression + '_1',
               'S.COMPLETION = NORMAL']
    children = []
    for index, child in enumerate(tree[1:3]):
        child_tag = tag + '_' + str(index)
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (porigin_' + child_tag + ')']
        child_value, number = value(checks, child_tag, child)
        checks += ['$coerce_number(' + child_value + ') = COERCED (NINT ' + number + ') false',
                   '$long_range(' + number + ')']
        children.append((child_value, number))
    result_number = integers.integer(tree[-1])
    result = 'PINT ' + result_number
    checks += ['$power_prepare(NINT ' + children[0][1] + ', NINT ' + children[1][1] + ') = POWERDONE (NINT ' + result_number + ') false',
               '$long_range(' + result_number + ')',
               '$binary_apply(S, POWER, ' + children[0][0] + ', ' + children[1][0] + ', 5) = S[.RESULT = KNOWN (' + result + ')]',
               '$string_read_runtime_value(S, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_bytes(S, ' + origin + ') = ($echo_value(' + result + '))']
    return result, result_number


module = prior
while module is not integers:
    module.value = value
    module = module.prior
integers.value, integers.TREES = value, TREES
conditions = prior.conditions


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
    report['scope'] = 'Four emitted integer-result POWER trees retain actual NORMAL/source/CODEfalse/read-eps/line/equal captured precision and recursively certified original typed operands. Quiet signed64 NINT coercions, exact POWERDONE(NINTi)false, fitting result and whole-state original typed binary_apply supply PINT VALUE and decimal BYTE. Genuine unary integer parents, BOOL/NULL inputs, base0 and iterative powers preserve real REQUEST keys1/-1/0/-4, returning Warning, supplied Throwable, bounds, owners, cleanup and budget rejoining. FLOAT operands/results, negative-exponent promotion, overflow, GENERAL and Deprecated remain outside this certificate. No06/09/33/387/compiler/numeric/cast/formatter/API/owner body or exact held-boundary change; saved native originals reused once and fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
