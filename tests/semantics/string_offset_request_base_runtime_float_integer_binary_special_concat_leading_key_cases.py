"""Fitting integral FLOAT integer operands retain real temporary key carriers."""
from pathlib import Path

import string_offset_request_base_float_boolnot_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
TRUE, FALSE = b'((!0.0) ? true : (1/0))', b'((!0.0) ? false : (1/0))'
NULL = b'((!INF) ? true : null)'
FLOAT_ONE, FLOAT_NEGATIVE = b'((!0.0) ? 1.0 : (1/0))', b'((!0.0) ? (-1.0) : (1/0))'
FLOAT_ZERO, FLOAT_NEGATIVE_ZERO = b'((!INF) ? (1/0) : 0.0)', b'((!INF) ? (1/0) : (-0.0))'
ONE = b'(+(!0.0))'
THREE = b'(' + ONE + b' + (' + ONE + b' + ' + ONE + b'))'
REPLACEMENTS = (
    ('string-offset-request-base-runtime-float-or-right-shift-leading-key', b"(('' . (!0.0)) . 'x')", b'((' + FLOAT_ONE + b' | ' + FLOAT_NEGATIVE_ZERO + b') >> ' + FLOAT_NEGATIVE_ZERO + b')'),
    ('string-offset-request-base-runtime-float-negative-and-xor-key', b"(('-' . (!(-0.0))) . 'x')", b'(~((+(' + FLOAT_NEGATIVE + b' & ' + FALSE + b')) ^ ' + NULL + b'))'),
    ('string-offset-marked-request-base-runtime-float-zero-left-shift-key-throw', b"(('0' . (!INF)) . 'x')", b'(' + FLOAT_ZERO + b' << ' + TRUE + b')'),
    ('string-offset-request-base-runtime-float-modulo-or-key-bounds', b"(('-4' . (!(1.0 + 2.0))) . 'x')", b'(~((+' + THREE + b') | (+(' + FLOAT_ONE + b' % ' + FLOAT_ONE + b'))))'),
)
CASES, OUTPUTS = {}, {}
for index, ((prior_name, source), (name, old, expression)) in enumerate(zip(prior.CASES.items(), REPLACEMENTS)):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    key = b'(( ' + expression + b' . ' + (b'null' if index == 0 else b'false') + b") . 'x')"
    CASES[name] = source.replace(old, key)
    OUTPUTS[name] = prior.OUTPUTS[prior_name]
