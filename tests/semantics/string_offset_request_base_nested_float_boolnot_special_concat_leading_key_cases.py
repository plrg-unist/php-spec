"""Nested runtime NOT preserves typed Boolean results without compiler folding."""
from pathlib import Path

import string_offset_request_base_float_boolnot_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
REPLACEMENTS = (
    (b"(('' . (!0.0)) . 'x')", b"(('1' . (!!0.0)) . 'x')"),
    (b"(('-' . (!(-0.0))) . 'x')", b"(('-1' . (!!(-0.0))) . 'x')"),
    (b"(('0' . (!INF)) . 'x')", b"(('0' . (!!!INF)) . 'x')"),
    (b"(('-4' . (!(1.0 + 2.0))) . 'x')", b"(('-4' . (!!!(1.0 + 2.0))) . 'x')"),
)
CASES, OUTPUTS = {}, {}
for (name, source), (old, new) in zip(prior.CASES.items(), REPLACEMENTS):
    assert source.count(old) == 1
    nested = name.replace('float-boolnot', 'nested-float-boolnot')
    CASES[nested] = source.replace(old, new)
    OUTPUTS[nested] = prior.OUTPUTS[name]
