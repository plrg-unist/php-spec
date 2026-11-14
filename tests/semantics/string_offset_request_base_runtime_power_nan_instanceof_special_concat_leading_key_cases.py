"""Completed emitted POWER NaN operands retain leading-key histories."""
from pathlib import Path

import string_offset_request_base_runtime_unary_nan_instanceof_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
NANS = (
    b'((-1.0)**(((float)(!0.0))/2.0))',
    b'(NAN**((float)(!0.0)))',
    b'(' + prior.prior.NANS[0] + b'**2.0)',
    b'(2.0**' + prior.prior.NANS[1] + b')',
)
NAMES = (
    'string-offset-request-base-runtime-power-nan-instanceof-leading-key',
    'string-offset-request-base-runtime-power-nan-instanceof-negative-key',
    'string-offset-marked-request-base-runtime-power-nan-instanceof-key-throw',
    'string-offset-request-base-runtime-power-nan-instanceof-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), old, name, operand in zip(prior.CASES.items(), prior.NANS, NAMES, NANS):
    assert source.count(old) == 1
    assert operand.count(b'(') == operand.count(b')')
    CASES[name] = source.replace(old, operand)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
