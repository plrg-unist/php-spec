"""Emitted FLOAT-cast NaN operands retain leading-key histories."""
from pathlib import Path

import string_offset_request_base_runtime_power_nan_instanceof_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
NANS = tuple(b'((float)' + operand + b')' for operand in (
    b'NAN', prior.prior.prior.NANS[1], prior.prior.NANS[2], prior.NANS[1],
))
NAMES = (
    'string-offset-request-base-runtime-float-cast-nan-instanceof-leading-key',
    'string-offset-request-base-runtime-float-cast-nan-instanceof-negative-key',
    'string-offset-marked-request-base-runtime-float-cast-nan-instanceof-key-throw',
    'string-offset-request-base-runtime-float-cast-nan-instanceof-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), old, name, operand in zip(prior.CASES.items(), prior.NANS, NAMES, NANS):
    assert source.count(old) == 1
    assert operand.count(b'(') == operand.count(b')')
    CASES[name] = source.replace(old, operand)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
