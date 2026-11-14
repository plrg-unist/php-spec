"""Quiet emitted BOOL/INT/FLOAT casts preserve typed key values."""
from pathlib import Path

import string_offset_request_base_float_boolnot_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
ONE, ZERO = b'(+(!0.0))', b'(+(!INF))'
REPLACEMENTS = (
    ('string-offset-request-base-runtime-cast-int-bool-leading-key', b"(('' . (!0.0)) . 'x')", b'((int)(!0.0))'),
    ('string-offset-request-base-runtime-cast-int-float-negative-key', b"(('-' . (!(-0.0))) . 'x')", b'((int)(-(1.5+' + ZERO + b')))'),
    ('string-offset-marked-request-base-runtime-cast-bool-integer-zero-key-throw', b"(('0' . (!INF)) . 'x')", b'(+((bool)' + ZERO + b'))'),
    ('string-offset-request-base-runtime-cast-float-bool-identity-negative-key-bounds', b"(('-4' . (!(1.0 + 2.0))) . 'x')", b'(~((((float)(!0.0))===1.0)+(' + ONE + b'+' + ONE + b')))'),
)
CASES, OUTPUTS = {}, {}
for index, ((prior_name, source), (name, old, expression)) in enumerate(zip(prior.CASES.items(), REPLACEMENTS)):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    key = b'(( ' + expression + b' . ' + (b'null' if index == 0 else b'false') + b") . 'x')"
    CASES[name] = source.replace(old, key)
    OUTPUTS[name] = prior.OUTPUTS[prior_name]
