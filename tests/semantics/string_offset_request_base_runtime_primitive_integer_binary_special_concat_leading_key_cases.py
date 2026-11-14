"""Quiet BOOL/NULL integer operators preserve actual temporary key carriers."""
from pathlib import Path

import string_offset_request_base_float_boolnot_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
TRUE, FALSE = b'((!0.0) ? true : (1/0))', b'((!0.0) ? false : (1/0))'
NULL = b'((!INF) ? true : null)'
ONE = b'(+(!0.0))'
THREE = b'(' + ONE + b' + (' + ONE + b' + ' + ONE + b'))'
REPLACEMENTS = (
    ('string-offset-request-base-runtime-primitive-or-right-shift-leading-key', b"(('' . (!0.0)) . 'x')", b'((' + TRUE + b' | ' + NULL + b') >> ' + NULL + b')'),
    ('string-offset-request-base-runtime-primitive-and-xor-negative-key', b"(('-' . (!(-0.0))) . 'x')", b'(~((+(' + TRUE + b' & ' + FALSE + b')) ^ ' + NULL + b'))'),
    ('string-offset-marked-request-base-runtime-primitive-null-left-shift-key-throw', b"(('0' . (!INF)) . 'x')", b'(' + NULL + b' << ' + TRUE + b')'),
    ('string-offset-request-base-runtime-primitive-modulo-or-key-bounds', b"(('-4' . (!(1.0 + 2.0))) . 'x')", b'(~((+' + THREE + b') | (+(' + TRUE + b' % ' + TRUE + b'))))'),
)
CASES, OUTPUTS = {}, {}
for index, ((prior_name, source), (name, old, expression)) in enumerate(zip(prior.CASES.items(), REPLACEMENTS)):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    key = b'(( ' + expression + b' . ' + (b'null' if index == 0 else b'false') + b") . 'x')"
    CASES[name] = source.replace(old, key)
    OUTPUTS[name] = prior.OUTPUTS[prior_name]
