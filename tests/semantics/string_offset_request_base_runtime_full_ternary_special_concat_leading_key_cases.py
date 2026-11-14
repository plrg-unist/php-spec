"""Quiet emitted full ternaries preserve selected typed key values."""
from pathlib import Path

import string_offset_request_base_float_boolnot_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
ONE, ZERO = b'(+(!0.0))', b'(+(!INF))'
CHOICE = b'((0.0+' + ZERO + b') ? (1/0) : (1.5+' + ZERO + b'))'
FLOAT_ONE = b'(' + ONE + b' ? ((float)(!0.0)) : (1/0))'
REPLACEMENTS = (
    ('string-offset-request-base-runtime-full-ternary-true-integer-leading-key', b"(('' . (!0.0)) . 'x')", b'((!0.0) ? ' + ONE + b' : (1/0))'),
    ('string-offset-request-base-runtime-full-ternary-false-integer-negative-key', b"(('-' . (!(-0.0))) . 'x')", b'(' + ZERO + b' ? (1/0) : (-(!0.0)))'),
    ('string-offset-marked-request-base-runtime-full-ternary-float-identity-zero-key-throw', b"(('0' . (!INF)) . 'x')", b'(+(' + CHOICE + b'===' + ONE + b'))'),
    ('string-offset-request-base-runtime-full-ternary-cast-float-negative-key-bounds', b"(('-4' . (!(1.0 + 2.0))) . 'x')", b'(~((' + FLOAT_ONE + b'===1.0)+(' + ONE + b'+' + ONE + b')))'),
)
CASES, OUTPUTS = {}, {}
for index, ((prior_name, source), (name, old, expression)) in enumerate(zip(prior.CASES.items(), REPLACEMENTS)):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    key = b'(( ' + expression + b' . ' + (b'null' if index == 0 else b'false') + b") . 'x')"
    CASES[name] = source.replace(old, key)
    OUTPUTS[name] = prior.OUTPUTS[prior_name]
