"""Strict-PINT emitted integer operators preserve the four Warning histories."""
from pathlib import Path

import string_offset_request_base_float_boolnot_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
REPLACEMENTS = (
    ('string-offset-request-base-runtime-integer-binary-mod-and-leading-key', b"(('' . (!0.0)) . 'x')", b"((+((+(!0.0)) % (+((!0.0) + (!0.0))))) & (+(!0.0)))"),
    ('string-offset-request-base-runtime-integer-binary-or-negative-leading-key', b"(('-' . (!(-0.0))) . 'x')", b"((+(~(+(!INF)))) | (+(!INF)))"),
    ('string-offset-marked-request-base-runtime-integer-binary-xor-zero-key-throw', b"(('0' . (!INF)) . 'x')", b"((+(!0.0)) ^ (+(!0.0)))"),
    ('string-offset-request-base-runtime-integer-binary-shifts-negative-key-bounds', b"(('-4' . (!(1.0 + 2.0))) . 'x')", b"((+((+(~((!0.0) + ((!0.0) + (!0.0))))) << (+(!0.0)))) >> (+(!0.0)))"),
)
CASES, OUTPUTS = {}, {}
for index, ((prior_name, source), (name, old, expression)) in enumerate(zip(prior.CASES.items(), REPLACEMENTS)):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    key = b'(( ' + expression + b' . ' + (b'null' if index == 0 else b'false') + b") . 'x')"
    CASES[name] = source.replace(old, key)
    OUTPUTS[name] = prior.OUTPUTS[prior_name]
