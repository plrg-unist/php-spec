#!/usr/bin/env python3
"""Intrinsic quiet FLOAT integer conversions retain original typed operands."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_float_integer_binary_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_primitive_integer_binary_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
FLOAT_ONE = ('TERNARY', prior.TRUTH, ('FLOAT', 4607182418800017408), True)
FLOAT_NEGATIVE = ('TERNARY', prior.TRUTH, ('FLOAT', 13830554455654793216), True)
FLOAT_ZERO = ('TERNARY', prior.prior.FALSE, ('FLOAT', 0), False)
FLOAT_NEGATIVE_ZERO = ('TERNARY', prior.prior.FALSE, ('FLOAT', 9223372036854775808), False)
TREES = (
    ('SHIFTRIGHT', ('BITOR', FLOAT_ONE, FLOAT_NEGATIVE_ZERO, 1), FLOAT_NEGATIVE_ZERO, 1),
    ('BITNOT', ('BITXOR', ('POSITIVE', ('BITAND', FLOAT_NEGATIVE, prior.FALSE, 0), 0), prior.NULL, 0), -1),
    ('SHIFTLEFT', FLOAT_ZERO, prior.TRUE, 0),
    ('BITNOT', ('BITOR', ('POSITIVE', prior.THREE, 3), ('POSITIVE', ('MODULO', FLOAT_ONE, FLOAT_ONE, 0), 0), 3), -4),
)
FLOAT_INTEGERS = {0: '0', 9223372036854775808: '0', 4607182418800017408: '1', 13830554455654793216: '$(-1)'}
base_value = prior.value


def value(checks, tag, tree):
    result, number = base_value(checks, tag, tree)
    if result.startswith('PFLOAT ') and int(result.removeprefix('PFLOAT ')) in FLOAT_INTEGERS:
        bits = result.removeprefix('PFLOAT ')
        number = FLOAT_INTEGERS[int(bits)]
        checks += ['$string_read_runtime_integer_quiet(' + result + ')',
                   '$float_long(' + bits + ', true) = (' + number + ', eps)']
        if tree[0] != 'FLOAT':
            checks += ['$string_read_runtime_bytes(S, porigin_' + tag + ') = eps']
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
    report['scope'] = 'Four emitted integer MOD/BW/shift trees admit fitting integral FLOAT values through a total quiet predicate with bits<2^64 and intrinsic float_long(bits,true) empty notices, explicit range and existing ordered full-state integer_coerce/original typed binary_apply. Both signed zeros and +/-1 keep exact bits before integer conversion; emitted FLOAT BYTE stays eps, compiled leaves retain existing literal byte routes and the actual PINT parent has decimal BYTE. New FLOAT requires NORMAL, preserving prior PINT completion independence and existing BOOL/NULL behavior. Genuine ternary/unary TMP, source/CODE/read-eps/line/equal precision, REQUEST keys1/-1/0/-4, Warning/Throwable/bounds/owners/cleanup/budgets remain. Only two current old FLOAT NORMAL controls promote, without replaying closed2649 evidence. Fractional/nonfinite/out-of-range/malformed FLOAT, string/owning and held lanes stay outside; no formatter/numeric/cast/compiler/API/owner body change. Saved native originals reused once; fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
