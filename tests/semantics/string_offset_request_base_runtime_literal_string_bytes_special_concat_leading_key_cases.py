"""Selected literal string bytes retain real temporary key carriers."""
from pathlib import Path

import string_offset_request_base_runtime_literal_string_integer_binary_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
EXPRESSIONS = (
    b"(((!0.0) ? '1' : (1/0)) ?: (1/0))",
    b"((+(!INF)) ? (1/0) : '-1')",
    b"(((!0.0) ? '0' : (1/0)) ?? (1/0))",
    b"((((!INF) ? true : null) ?? '0') ?: '-4')",
)
NAMES = (
    'string-offset-request-base-runtime-literal-string-truthy-shorthand-leading-key',
    'string-offset-request-base-runtime-literal-string-false-ternary-negative-key',
    'string-offset-marked-request-base-runtime-literal-string-nonnull-coalesce-key-throw',
    'string-offset-request-base-runtime-literal-string-null-coalesce-falsey-shorthand-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), old, name, expression in zip(prior.CASES.items(), prior.EXPRESSIONS, NAMES, EXPRESSIONS):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    CASES[name] = source.replace(old, expression)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
