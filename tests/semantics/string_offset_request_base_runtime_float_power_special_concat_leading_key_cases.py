"""Completed nonNaN FLOAT powers retain actual temporary key carriers."""
from pathlib import Path

import string_offset_request_base_runtime_integer_power_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
ONE, TRUE, NULL = prior.ONE, prior.TRUE, prior.NULL
FLOAT_TWO = b'((!0.0) ? 2.0 : (1/0))'
FLOAT_NEGATIVE_ZERO = b'(-((float)(+(!INF))))'
EXPRESSIONS = (
    b'(+((' + FLOAT_TWO + b' ** ' + NULL + b') === 1.0))',
    b'(~((int)(' + FLOAT_NEGATIVE_ZERO + b' ** ' + TRUE + b')))',
    b'((int)(INF ** (-' + ONE + b')))',
    b'(~((+((' + TRUE + b' ** 0.0) === 1.0)) + (' + ONE + b' + ' + ONE + b')))',
)
NAMES = (
    'string-offset-request-base-runtime-float-null-power-leading-key',
    'string-offset-request-base-runtime-negative-zero-bool-power-negative-key',
    'string-offset-marked-request-base-runtime-infinity-negative-power-key-throw',
    'string-offset-request-base-runtime-bool-float-zero-power-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), old, name, expression in zip(prior.CASES.items(), prior.EXPRESSIONS, NAMES, EXPRESSIONS):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    CASES[name] = source.replace(old, expression)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
