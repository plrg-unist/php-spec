"""Runtime signs over typed NOT results retain real temporary key carriers."""
from pathlib import Path

import string_offset_request_base_float_boolnot_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
REPLACEMENTS = (
    (b"(('' . (!0.0)) . 'x')", b"(((+(!0.0)) . null) . 'x')"),
    (b"(('-' . (!(-0.0))) . 'x')", b"(((-(!(-0.0))) . false) . 'x')"),
    (b"(('0' . (!INF)) . 'x')", b"(((+(!INF)) . false) . 'x')"),
    (b"(('-4' . (!(1.0 + 2.0))) . 'x')", b"(('-4' . (!(-(!0.0)))) . 'x')"),
)
CASES, OUTPUTS = {}, {}
for (name, source), (old, new) in zip(prior.CASES.items(), REPLACEMENTS):
    assert source.count(old) == 1
    signed = name.replace('float-boolnot', 'runtime-unary-integer')
    CASES[signed] = source.replace(old, new)
    OUTPUTS[signed] = prior.OUTPUTS[name]
