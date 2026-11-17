"""Quiet null-left coalesce selects exact NaN instanceof fallbacks."""
from pathlib import Path

import string_offset_request_base_runtime_arithmetic_nan_instanceof_special_concat_leading_key_cases as arithmetic
import string_offset_request_base_runtime_unary_nan_instanceof_special_concat_leading_key_cases as unary
import string_offset_request_base_runtime_float_cast_nan_instanceof_special_concat_leading_key_cases as casts
import string_offset_request_base_runtime_false_shorthand_nan_instanceof_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
NANS = (
    b'(((!INF) ? true : null) ?? NAN)',
    b'(((!INF) ?: null) ?? ' + arithmetic.NANS[1] + b')',
    b'((((!INF) ? true : null) ?? null) ?? ' + unary.NANS[2] + b')',
    b'(((!INF) ? true : null) ?? ' + casts.NANS[0] + b')',
)
NAMES = (
    'string-offset-request-base-runtime-null-left-nan-coalesce-instanceof-leading-key',
    'string-offset-request-base-runtime-null-left-nan-coalesce-instanceof-negative-key',
    'string-offset-marked-request-base-runtime-null-left-nan-coalesce-instanceof-key-throw',
    'string-offset-request-base-runtime-null-left-nan-coalesce-instanceof-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), old, name, operand in zip(prior.CASES.items(), prior.NANS, NAMES, NANS):
    assert source.count(old) == 1
    assert operand.count(b'(') == operand.count(b')')
    CASES[name] = source.replace(old, operand)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
