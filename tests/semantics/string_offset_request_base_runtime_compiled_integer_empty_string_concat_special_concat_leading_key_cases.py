"""Compiled integer CONCAT survivors retain their actual immutable headers."""
from pathlib import Path

import string_offset_request_base_runtime_primitive_empty_string_concat_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
EXPRESSIONS = (
    b"((int)(((5 + 5) . (!INF)) === '10'))",
    b'((int)((!INF) . (-1)))',
    b"((int)((9223372036854775807 . (!INF)) === '0'))",
    b'((int)((!INF) . (-4)))',
)
NAMES = (
    'string-offset-request-base-runtime-compiled-integer-empty-string-concat-leading-key',
    'string-offset-request-base-runtime-compiled-negative-empty-string-concat-key',
    'string-offset-marked-request-base-runtime-compiled-max-empty-string-concat-key-throw',
    'string-offset-request-base-runtime-compiled-negative-empty-string-concat-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), old, name, expression in zip(prior.CASES.items(), prior.EXPRESSIONS, NAMES, EXPRESSIONS):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    CASES[name] = source.replace(old, expression)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
