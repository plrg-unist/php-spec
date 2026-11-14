"""Runtime empty-string concatenations retain existing interned headers."""
from pathlib import Path

import string_offset_request_base_runtime_one_byte_string_bitwise_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
EMPTY = b'((string)(!INF))'
EXPRESSIONS = (
    b"((int)((" + EMPTY + b" . ((!0.0) ? '1' : (1/0))) === '1'))",
    b"(~((int)('0' . " + EMPTY + b')))',
    b'((int)(' + EMPTY + b' . ' + EMPTY + b'))',
    b"(~((int)((((!0.0) ? '003' : (1/0)) . " + EMPTY + b') . ' + EMPTY + b')))',
)
NAMES = (
    'string-offset-request-base-runtime-empty-left-string-concat-leading-key',
    'string-offset-request-base-runtime-empty-right-string-concat-negative-key',
    'string-offset-marked-request-base-runtime-both-empty-string-concat-key-throw',
    'string-offset-request-base-runtime-nested-empty-string-concat-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), old, name, expression in zip(prior.CASES.items(), prior.EXPRESSIONS, NAMES, EXPRESSIONS):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    CASES[name] = source.replace(old, expression)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
