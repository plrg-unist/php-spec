"""Emitted NULL contributes empty bytes to real concatenated key carriers."""
from pathlib import Path

import string_offset_request_base_float_boolnot_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
REPLACEMENTS = (
    ('string-offset-request-base-runtime-null-full-false-byte-leading-key', b"(('' . (!0.0)) . 'x')", b'((!INF) ? true : null)', b'1'),
    ('string-offset-request-base-runtime-null-shorthand-byte-negative-key', b"(('-' . (!(-0.0))) . 'x')", b'((!INF) ?: null)', b'-1'),
    ('string-offset-marked-request-base-runtime-null-coalesce-byte-key-throw', b"(('0' . (!INF)) . 'x')", b'(((!INF) ? true : null) ?? null)', b'0'),
    ('string-offset-request-base-runtime-null-full-true-byte-key-bounds', b"(('-4' . (!(1.0 + 2.0))) . 'x')", b'((!0.0) ? null : (1/0))', b'-4'),
)
CASES, OUTPUTS = {}, {}
for (prior_name, source), (name, old, expression, digits) in zip(prior.CASES.items(), REPLACEMENTS):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    key = b'(( ' + expression + b" . '" + digits + b"') . 'x')"
    CASES[name] = source.replace(old, key)
    OUTPUTS[name] = prior.OUTPUTS[prior_name]
