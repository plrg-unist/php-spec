"""Nonnull NaN coalesce operands preserve skipped-RHS leading-key histories."""
from pathlib import Path

import string_offset_request_base_runtime_arithmetic_nan_instanceof_special_concat_leading_key_cases as arithmetic
import string_offset_request_base_runtime_unary_nan_instanceof_special_concat_leading_key_cases as unary
import string_offset_request_base_runtime_float_cast_nan_instanceof_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
NANS = tuple(b'(' + left + b' ?? ' + right + b')' for left, right in zip(
    (b'NAN', arithmetic.NANS[1], unary.NANS[2], prior.NANS[3]),
    (b'(1/0)', b'("2junk"*2)', b'(!NAN)', b'7.5'),
))
NAMES = (
    'string-offset-request-base-runtime-nonnull-nan-coalesce-instanceof-leading-key',
    'string-offset-request-base-runtime-nonnull-nan-coalesce-instanceof-negative-key',
    'string-offset-marked-request-base-runtime-nonnull-nan-coalesce-instanceof-key-throw',
    'string-offset-request-base-runtime-nonnull-nan-coalesce-instanceof-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), old, name, operand in zip(prior.CASES.items(), prior.NANS, NAMES, NANS):
    assert source.count(old) == 1
    assert operand.count(b'(') == operand.count(b')')
    CASES[name] = source.replace(old, operand)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
