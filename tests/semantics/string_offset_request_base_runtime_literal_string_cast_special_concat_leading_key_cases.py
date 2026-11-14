"""Explicit literal-string casts retain actual temporary key carriers."""
from pathlib import Path

import string_offset_request_base_runtime_literal_string_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
EXPRESSIONS = (
    b"((int)((!0.0) ? '1tail' : (1/0)))",
    b"(~((int)((!0.0) ? 'junk' : (1/0))))",
    b"(+((bool)((!0.0) ? '0' : (1/0))))",
    b"(~((int)((float)((!0.0) ? '3.0tail' : (1/0)))))",
)
NAMES = (
    'string-offset-request-base-runtime-literal-string-int-prefix-leading-key',
    'string-offset-request-base-runtime-literal-string-int-nonnumeric-negative-key',
    'string-offset-marked-request-base-runtime-literal-string-bool-key-throw',
    'string-offset-request-base-runtime-literal-string-float-prefix-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), old, name, expression in zip(prior.CASES.items(), prior.EXPRESSIONS, NAMES, EXPRESSIONS):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    CASES[name] = source.replace(old, expression)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
