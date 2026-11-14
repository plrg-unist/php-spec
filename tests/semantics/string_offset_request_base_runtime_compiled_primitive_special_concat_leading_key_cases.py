"""Identity-certified compiled primitives compose through emitted key parents."""
from pathlib import Path

import string_offset_request_base_float_boolnot_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
TRUTH, FALSE = b'(!0.0)', b'(!INF)'
REPLACEMENTS = (
    ('string-offset-request-base-runtime-compiled-boolean-selected-leading-key', b"(('' . (!0.0)) . 'x')", b'(+(( ' + TRUTH + b' ? true : (1/0))===' + TRUTH + b'))'),
    ('string-offset-request-base-runtime-compiled-negative-integer-fallback-key', b"(('-' . (!(-0.0))) . 'x')", b'(' + FALSE + b' ?: (-1))'),
    ('string-offset-marked-request-base-runtime-compiled-null-identity-zero-key-throw', b"(('0' . (!INF)) . 'x')", b'(+(( ' + FALSE + b' ?: null)===' + FALSE + b'))'),
    ('string-offset-request-base-runtime-compiled-folded-integer-selected-bounds', b"(('-4' . (!(1.0 + 2.0))) . 'x')", b'(~(' + TRUTH + b' ? (1+2) : (1/0)))'),
)
CASES, OUTPUTS = {}, {}
for index, ((prior_name, source), (name, old, expression)) in enumerate(zip(prior.CASES.items(), REPLACEMENTS)):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    key = b'(( ' + expression + b' . ' + (b'null' if index == 0 else b'false') + b") . 'x')"
    CASES[name] = source.replace(old, key)
    OUTPUTS[name] = prior.OUTPUTS[prior_name]
