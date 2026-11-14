"""Quiet emitted integer arithmetic and BITNOT retain real key carriers."""
from pathlib import Path

import string_offset_request_base_float_boolnot_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
REPLACEMENTS = (
    ('string-offset-request-base-runtime-integer-operator-add-leading-key', b"(('' . (!0.0)) . 'x')", b"((((!0.0) + (+(!INF))) . null) . 'x')"),
    ('string-offset-request-base-runtime-integer-operator-subtract-negative-leading-key', b"(('-' . (!(-0.0))) . 'x')", b"((((+(!INF)) - (!0.0)) . false) . 'x')"),
    ('string-offset-marked-request-base-runtime-integer-operator-multiply-zero-key-throw', b"(('0' . (!INF)) . 'x')", b"((((+(!INF)) * (-(!0.0))) . false) . 'x')"),
    ('string-offset-request-base-runtime-integer-operator-bitnot-add-negative-key-bounds', b"(('-4' . (!(1.0 + 2.0))) . 'x')", b"(((~((!0.0) + ((!0.0) + (!0.0)))) . false) . 'x')"),
)
CASES, OUTPUTS = {}, {}
for (prior_name, source), (name, old, new) in zip(prior.CASES.items(), REPLACEMENTS):
    assert source.count(old) == 1
    CASES[name] = source.replace(old, new)
    OUTPUTS[name] = prior.OUTPUTS[prior_name]
