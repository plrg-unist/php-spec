"""Exact NULL cast operands compose through emitted key parents."""
from pathlib import Path

import string_offset_request_base_float_boolnot_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
REPLACEMENTS = (
    ('string-offset-request-base-runtime-null-bool-cast-selected-leading-key', b"(('' . (!0.0)) . 'x')", b'(+(((bool)((!INF) ? true : null)) === (!INF)))'),
    ('string-offset-request-base-runtime-null-int-cast-shorthand-negative-key', b"(('-' . (!(-0.0))) . 'x')", b'(~((int)((!INF) ?: null)))'),
    ('string-offset-marked-request-base-runtime-null-float-cast-coalesce-key-throw', b"(('0' . (!INF)) . 'x')", b'((int)((float)(((!INF) ? true : null) ?? null)))'),
    ('string-offset-request-base-runtime-null-int-cast-raw-key-bounds', b"(('-4' . (!(1.0 + 2.0))) . 'x')", b'(~(((int)null) + (+(!0.0) + (+(!0.0) + +(!0.0)))))'),
)
CASES, OUTPUTS = {}, {}
for index, ((prior_name, source), (name, old, expression)) in enumerate(zip(prior.CASES.items(), REPLACEMENTS)):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    key = b'(( ' + expression + b' . ' + (b'null' if index == 0 else b'false') + b") . 'x')"
    CASES[name] = source.replace(old, key)
    OUTPUTS[name] = prior.OUTPUTS[prior_name]
