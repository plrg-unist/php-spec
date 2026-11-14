"""One-byte string bitwise results retain real temporary key carriers."""
from pathlib import Path

import string_offset_request_base_runtime_interned_string_cast_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
EXPRESSIONS = (
    b"((int)((((!0.0) ? '1' : (1/0)) & '3') === '1'))",
    b"(~((int)(((!0.0) ? '0' : (1/0)) | '0')))",
    b"((int)(~((!0.0) ? '1' : (1/0))))",
    b"(~((int)(((!0.0) ? 'p' : (1/0)) ^ 'C')))",
)
NAMES = (
    'string-offset-request-base-runtime-one-byte-string-and-leading-key',
    'string-offset-request-base-runtime-one-byte-string-or-negative-key',
    'string-offset-marked-request-base-runtime-one-byte-string-not-key-throw',
    'string-offset-request-base-runtime-one-byte-string-xor-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), old, name, expression in zip(prior.CASES.items(), prior.EXPRESSIONS, NAMES, EXPRESSIONS):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    CASES[name] = source.replace(old, expression)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
