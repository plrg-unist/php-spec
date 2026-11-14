"""Emitted quiet AND/OR keeps selected truth and skips error-producing RHSs."""
from pathlib import Path

import string_offset_request_base_float_boolnot_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
REPLACEMENTS = (
    ('string-offset-request-base-runtime-or-skipped-error-leading-key', b"(('' . (!0.0)) . 'x')", b"((!0.0) || (1 / 0))"),
    ('string-offset-request-base-runtime-logical-and-float-negative-leading-key', b"(('-' . (!(-0.0))) . 'x')", b"(-((+(!0.0)) and INF))"),
    ('string-offset-marked-request-base-runtime-and-skipped-error-zero-key-throw', b"(('0' . (!INF)) . 'x')", b"(+((!INF) && (1 / 0)))"),
    ('string-offset-request-base-runtime-nested-logical-or-negative-key-bounds', b"(('-4' . (!(1.0 + 2.0))) . 'x')", b"(~(((!INF) or (+(!0.0))) + (((!0.0) && (+(!0.0))) + ((+(!INF)) || (!0.0)))))"),
)
CASES, OUTPUTS = {}, {}
for (prior_name, source), (name, old, expression) in zip(prior.CASES.items(), REPLACEMENTS):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    key = b'(( ' + expression + b' . ' + (b'null' if not CASES else b'false') + b") . 'x')"
    CASES[name] = source.replace(old, key)
    OUTPUTS[name] = prior.OUTPUTS[prior_name]
