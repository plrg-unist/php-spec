"""Literal INTERNED string operands retain actual temporary key carriers."""
from pathlib import Path

import string_offset_request_base_runtime_float_power_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
ZERO, ONE = b'(+(!INF))', b'(+(!0.0))'
EXPRESSIONS = (
    b"(+('1' + " + ZERO + b'))',
    b"(~('0' - " + ZERO + b'))',
    b"(+(('01') === " + ONE + b'))',
    b"(~('3' * " + ONE + b'))',
)
NAMES = (
    'string-offset-request-base-runtime-literal-string-add-leading-key',
    'string-offset-request-base-runtime-literal-string-subtract-negative-key',
    'string-offset-marked-request-base-runtime-literal-string-identity-key-throw',
    'string-offset-request-base-runtime-literal-string-multiply-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), old, name, expression in zip(prior.CASES.items(), prior.EXPRESSIONS, NAMES, EXPRESSIONS):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    CASES[name] = source.replace(old, expression)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
