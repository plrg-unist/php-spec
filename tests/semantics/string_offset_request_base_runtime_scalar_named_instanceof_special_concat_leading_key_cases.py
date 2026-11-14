"""Quiet scalar named-instanceof results retain existing leading-key histories."""
from pathlib import Path

import string_offset_request_base_runtime_compiled_integer_empty_string_concat_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
EXPRESSIONS = (
    b'((int)(((!0.0) instanceof stdClass) === (!INF)))',
    b'(~((int)((!INF) instanceof MissingStringReadTarget)))',
    b"((int)((((!0.0) ? 'x' : (1/0))) instanceof stdClass))",
    b'(~(((int)(((+(!0.0)) instanceof MissingStringReadTarget) === (!INF))) + (1 + 1)))',
)
NAMES = (
    'string-offset-request-base-runtime-scalar-named-instanceof-leading-key',
    'string-offset-request-base-runtime-scalar-named-instanceof-negative-key',
    'string-offset-marked-request-base-runtime-string-named-instanceof-key-throw',
    'string-offset-request-base-runtime-integer-named-instanceof-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), old, name, expression in zip(prior.CASES.items(), prior.EXPRESSIONS, NAMES, EXPRESSIONS):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    CASES[name] = source.replace(old, expression)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
