"""Quiet emitted FLOAT signs feed typed parents without a BYTE receipt."""
from pathlib import Path

import string_offset_request_base_float_boolnot_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
ONE, ZERO = b'(+(!0.0))', b'(+(!INF))'
REPLACEMENTS = (
    ('string-offset-request-base-runtime-float-negative-zero-not-leading-key', b"(('' . (!0.0)) . 'x')", b'(!(-(' + ZERO + b'+(-0.0))))'),
    ('string-offset-request-base-runtime-float-positive-zero-identity-negative-key', b"(('-' . (!(-0.0))) . 'x')", b'(-((+(' + ONE + b'-1.0))===(-0.0)))'),
    ('string-offset-marked-request-base-runtime-float-positive-fraction-identity-zero-key-throw', b"(('0' . (!INF)) . 'x')", b'(+((+(' + ONE + b'*1.5))===' + ONE + b'))'),
    ('string-offset-request-base-runtime-float-nested-sign-identity-negative-key-bounds', b"(('-4' . (!(1.0 + 2.0))) . 'x')", b'(~(((+(-(INF+' + ZERO + b')))===(-INF))+(' + ONE + b'+' + ONE + b')))'),
)
CASES, OUTPUTS = {}, {}
for (prior_name, source), (name, old, expression) in zip(prior.CASES.items(), REPLACEMENTS):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    key = b'(( ' + expression + b' . ' + (b'null' if len(CASES) == 0 else b'false') + b") . 'x')"
    CASES[name] = source.replace(old, key)
    OUTPUTS[name] = prior.OUTPUTS[prior_name]
