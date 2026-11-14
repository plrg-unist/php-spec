"""Immutable explicit string casts retain real temporary key carriers."""
from pathlib import Path

import string_offset_request_base_runtime_literal_string_bytes_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
ONE = b'(+(!0.0))'
THREE = b'(' + ONE + b' + (' + ONE + b' + ' + ONE + b'))'
EXPRESSIONS = (
    b'((string)(!0.0))',
    b'(~((int)((string)(!INF))))',
    b'((int)((string)((!INF) ? true : null)))',
    b'(~((int)((string)((string)(+' + THREE + b')))))',
)
NAMES = (
    'string-offset-request-base-runtime-interned-string-cast-true-leading-key',
    'string-offset-request-base-runtime-interned-string-cast-false-negative-key',
    'string-offset-marked-request-base-runtime-interned-string-cast-null-key-throw',
    'string-offset-request-base-runtime-interned-string-cast-digit-identity-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), old, name, expression in zip(prior.CASES.items(), prior.EXPRESSIONS, NAMES, EXPRESSIONS):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    CASES[name] = source.replace(old, expression)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
