"""Quiet emitted FLOAT arithmetic feeds typed truth and identity, without BYTE."""
from pathlib import Path

import string_offset_request_base_float_boolnot_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
REPLACEMENTS = (
    ('string-offset-request-base-runtime-float-add-not-leading-key', b"(('' . (!0.0)) . 'x')", b"(!((+(!INF)) + (-0.0)))"),
    ('string-offset-request-base-runtime-float-sub-identity-negative-leading-key', b"(('-' . (!(-0.0))) . 'x')", b"(-(((+(!0.0)) - 1.0) === 0.0))"),
    ('string-offset-marked-request-base-runtime-float-mul-identity-zero-key-throw', b"(('0' . (!INF)) . 'x')", b"(+(((+(!0.0)) * 1.5) === (+(!0.0))))"),
    ('string-offset-request-base-runtime-float-div-nested-identity-negative-key-bounds', b"(('-4' . (!(1.0 + 2.0))) . 'x')", b"(~(((1.0 / ((+(!0.0)) + (+(!0.0)))) === 0.5) + ((((!0.0) + 0.0) === 1.0) + ((1.0 - (+(!0.0))) === 0.0))))"),
)
CASES, OUTPUTS = {}, {}
for index, ((prior_name, source), (name, old, expression)) in enumerate(zip(prior.CASES.items(), REPLACEMENTS)):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    key = b'(( ' + expression + b' . ' + (b'null' if index == 0 else b'false') + b") . 'x')"
    CASES[name] = source.replace(old, key)
    OUTPUTS[name] = prior.OUTPUTS[prior_name]
