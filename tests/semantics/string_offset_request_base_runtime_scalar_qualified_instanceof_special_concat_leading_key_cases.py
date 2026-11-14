"""Exact qualified scalar-instanceof results retain leading-key histories."""
from pathlib import Path

import string_offset_request_base_runtime_scalar_named_instanceof_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
EXPRESSIONS = (
    b'((int)(((!0.0) instanceof \\stdClass) === (!INF)))',
    b'(~((int)((!INF) instanceof \\MissingStringRead\\Target)))',
    b"((int)((((!0.0) ? 'x' : (1/0))) instanceof MissingStringRead\\Target))",
    b'(~(((int)(((+(!0.0)) instanceof MissingStringRead\\Deep\\Target) === (!INF))) + (1 + 1)))',
)
NAMES = (
    'string-offset-request-base-runtime-scalar-qualified-instanceof-leading-key',
    'string-offset-request-base-runtime-scalar-qualified-instanceof-negative-key',
    'string-offset-marked-request-base-runtime-string-qualified-instanceof-key-throw',
    'string-offset-request-base-runtime-integer-qualified-instanceof-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), old, name, expression in zip(prior.CASES.items(), prior.EXPRESSIONS, NAMES, EXPRESSIONS):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    CASES[name] = source.replace(old, expression)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
