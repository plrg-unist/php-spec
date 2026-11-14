#!/usr/bin/env python3
"""Quiet POWERDONE FLOAT values retain exact bits and no BYTE receipt."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_float_arithmetic_special_concat_leading_key_protocol as arithmetic
import string_offset_request_base_runtime_float_power_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_integer_power_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
FLOAT_TWO = ('TERNARY', prior.TRUE[1], ('FLOAT', 4611686018427387904), True)
TREES = (
    ('POSITIVE', ('IDENTICAL', ('FLOAT_POWER', FLOAT_TWO, prior.NULL, 4607182418800017408), ('FLOAT', 4607182418800017408), True), 1),
    ('BITNOT', ('CAST', 'CASTINT', ('FLOAT_POWER', prior.prior.FLOAT_NEGATIVE_ZERO, prior.TRUE, 9223372036854775808), 'PINT 0'), -1),
    ('CAST', 'CASTINT', ('FLOAT_POWER', ('FLOAT', 9218868437227405312), ('NEGATIVE', prior.ONE, -1), 0), 'PINT 0'),
    ('BITNOT', ('ADD', ('POSITIVE', ('IDENTICAL', ('FLOAT_POWER', prior.TRUE, ('FLOAT', 0), 4607182418800017408), ('FLOAT', 4607182418800017408), True), 1), ('ADD', prior.ONE, prior.ONE, 2), 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[0] != 'FLOAT_POWER':
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
        child_value = value(checks, child_tag, child)[0]
        number = 'NINT 0' if child_value == 'PNULL' else arithmetic.numeric(child_value)
        checks += ['$coerce_number(' + child_value + ') = COERCED (' + number + ') false']
        children.append((child_value, number))
    bits = str(tree[-1])
    result = 'PFLOAT ' + bits
    truth = str(tree[-1] not in (0, 9223372036854775808)).lower()
    checks += ['$power_prepare(' + children[0][1] + ', ' + children[1][1] + ') = POWERDONE (NFLOAT ' + bits + ') false',
               '$number_bool(NFLOAT ' + bits + ') = (' + truth + ', false)',
               '$binary_apply(S, POWER, ' + children[0][0] + ', ' + children[1][0] + ', 5) = S[.RESULT = KNOWN (' + result + ')]',
               '$string_read_runtime_value(S, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_bytes(S, ' + origin + ') = eps']
    return result, None


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
    report['scope'] = 'Four emitted completed nonNaN FLOAT POWER values retain actual NORMAL/source/CODEfalse/read-eps/line/equal captured precision, recursive original typed operands, quiet numeric coercions, POWERDONE(NFLOATbits)false, exact nonNaN bits/truth and full-state original typed binary_apply. FLOAT2**NULL and BOOL**FLOAT0 retain FLOAT1 identity; FLOAT-0**BOOL retains negative zero; INF**negative PINT yields positive zero. Existing typed parents form REQUEST keys1/-1/0/-4 with captured precision, returning Warning, supplied Throwable, bounds, owners, cleanup and budget rejoining. Emitted FLOAT BYTE remains eps; INT results, GENERAL, NaN and Deprecated power stay separate. No06/09/33/387/compiler/numeric/cast/formatter/API/owner body or exact held-boundary change; saved native originals reused once and fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
