"""Full ternaries preserve only their selected NaN instanceof operands."""
from pathlib import Path

import string_offset_request_base_runtime_arithmetic_nan_instanceof_special_concat_leading_key_cases as arithmetic
import string_offset_request_base_runtime_unary_nan_instanceof_special_concat_leading_key_cases as unary
import string_offset_request_base_runtime_nonnull_nan_coalesce_instanceof_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
NANS = (
    b'((!0.0) ? NAN : (1/0))',
    b'((+(!INF)) ? ("2junk"*2) : ' + arithmetic.NANS[1] + b')',
    b'((0.0+(+(!0.0))) ? ' + unary.NANS[2] + b' : (!NAN))',
    b'((0.0+(+(!INF))) ? 7.5 : ' + prior.NANS[3] + b')',
)
NAMES = (
    'string-offset-request-base-runtime-full-ternary-nan-instanceof-leading-key',
    'string-offset-request-base-runtime-full-ternary-nan-instanceof-negative-key',
    'string-offset-marked-request-base-runtime-full-ternary-nan-instanceof-key-throw',
    'string-offset-request-base-runtime-full-ternary-nan-instanceof-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), old, name, operand in zip(prior.CASES.items(), prior.NANS, NAMES, NANS):
    assert source.count(old) == 1
    assert operand.count(b'(') == operand.count(b')')
    CASES[name] = source.replace(old, operand)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
