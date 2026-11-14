"""Quiet completed integer powers retain actual temporary key carriers."""
from pathlib import Path

import string_offset_request_base_runtime_float_bitnot_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
ONE, THREE, TRUE, NULL = prior.prior.ONE, prior.prior.THREE, prior.prior.TRUE, prior.prior.NULL
EXPRESSIONS = (
    b'(+(' + ONE + b' ** ' + THREE + b'))',
    b'(~((+(!INF)) ** ' + ONE + b'))',
    b'(+(' + NULL + b' ** ' + TRUE + b'))',
    b'(~(' + THREE + b' ** ' + ONE + b'))',
)
NAMES = (
    'string-offset-request-base-runtime-integer-power-leading-key',
    'string-offset-request-base-runtime-integer-zero-power-negative-key',
    'string-offset-marked-request-base-runtime-null-bool-power-key-throw',
    'string-offset-request-base-runtime-integer-three-power-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), old, name, expression in zip(prior.CASES.items(), prior.EXPRESSIONS, NAMES, EXPRESSIONS):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    CASES[name] = source.replace(old, expression)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
