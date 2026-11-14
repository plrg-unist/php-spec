"""Emitted unary NaN instanceof operands retain leading-key histories."""
from pathlib import Path

import string_offset_request_base_runtime_arithmetic_nan_instanceof_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
NANS = tuple(b'(' + sign + operand + b')' for sign, operand in zip((b'+', b'-', b'+', b'-'), prior.NANS))
NAMES = (
    'string-offset-request-base-runtime-unary-nan-instanceof-leading-key',
    'string-offset-request-base-runtime-unary-nan-instanceof-negative-key',
    'string-offset-marked-request-base-runtime-unary-nan-instanceof-key-throw',
    'string-offset-request-base-runtime-unary-nan-instanceof-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), old, name, operand in zip(prior.CASES.items(), prior.NANS, NAMES, NANS):
    assert source.count(old) == 1
    assert operand.count(b'(') == operand.count(b')')
    CASES[name] = source.replace(old, operand)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
