#!/usr/bin/env python3
"""Quiet FLOAT bitwise NOT retains the original typed operand and key owners."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_float_bitnot_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_float_integer_binary_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
FLOAT_NEGATIVE_TWO = ('TERNARY', prior.prior.TRUTH, ('FLOAT', 13835058055282163712), True)
FLOAT_NEGATIVE_ZERO = ('FLOAT_UNARY', 'NEGATIVE', ('CAST', 'CASTFLOAT', ('POSITIVE', ('NOT', ('FLOAT', 9218868437227405312), False), 0), 'PFLOAT 0'), 9223372036854775808)
FLOAT_NEGATIVE_ONE = ('FLOAT_UNARY', 'NEGATIVE', prior.FLOAT_ONE, 13830554455654793216)
FLOAT_THREE = ('FLOAT_BINARY', 'ADD', prior.FLOAT_ONE, ('FLOAT', 4611686018427387904), 4613937818241073152)
TREES = tuple(('BITNOT', child, result) for child, result in zip(
    (FLOAT_NEGATIVE_TWO, FLOAT_NEGATIVE_ZERO, FLOAT_NEGATIVE_ONE, FLOAT_THREE), (1, -1, 0, -4)))
FLOAT_INTEGERS = {**prior.FLOAT_INTEGERS, 13835058055282163712: '$(-2)', 4611686018427387904: '2', 4613937818241073152: '3'}
base_value = prior.value


def value(checks, tag, tree):
    if tree[0] != 'BITNOT':
        result, number = base_value(checks, tag, tree)
        if result.startswith('PFLOAT '):
            number = FLOAT_INTEGERS.get(int(result.removeprefix('PFLOAT ')), number)
        return result, number
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    integers.emitted(checks, tag)
    checks += ['$pfshape(' + expression + ') = PFBITNOT ' + expression + '_0',
               '$origin_child((' + origin + '), [PCFIELD 0]) = (porigin_' + tag + '_0)']
    child, child_number = value(checks, tag + '_0', tree[1])
    assert child.startswith(('PINT ', 'PFLOAT ')) and child_number is not None
    number = integers.integer(tree[-1])
    result = 'PINT ' + number
    checks += ['$string_read_runtime_integer_quiet(' + child + ')',
               '$integer_coerce(S, ' + child + ', 5) = S[.RESULT = KNOWN (PINT ' + child_number + ')]',
               '$long_range(' + child_number + ')', '$long_not(' + child_number + ') = ' + number,
               '$long_range(' + number + ')',
               '$bitnot_value(S, ' + child + ', 5) = S[.RESULT = KNOWN (' + result + ')]',
               '$string_read_runtime_value(S, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_bytes(S, ' + origin + ') = ($echo_value(' + result + '))']
    if child.startswith('PFLOAT '):
        checks += ['S.COMPLETION = NORMAL',
                   '$float_long(' + child.removeprefix('PFLOAT ') + ', true) = (' + child_number + ', eps)',
                   '$string_read_runtime_bytes(S, porigin_' + tag + '_0) = eps']
    return result, number


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
    report['scope'] = 'Four emitted BITNOT trees admit fitting integral FLOAT values through exact int/float tags, intrinsic integer_quiet and whole-state integer_coerce, fitting long_not and original typed full-state bitnot_value. New FLOAT requires NORMAL; prior PINT completion independence remains. Actual ternary, CASTFLOAT, unary minus and FLOAT ADD producers retain exact source/CODE/read-eps/line/equal precision and PFLOAT bits; emitted FLOAT BYTE stays eps and the resulting PINT has decimal BYTE. REQUEST keys1/-1/0/-4 preserve returning Warning, supplied Throwable, bounds, owners, cleanup and budget rejoining. BOOL/NULL/string/owning and fractional/nonfinite/out-of-range/malformed FLOAT operands remain outside this integer-result certificate. No57/387/compiler/numeric/cast/formatter/API/owner body or exact held-boundary change; saved native originals reused once and fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
