"""Quiet emitted FLOAT bitwise NOT retains real temporary key carriers."""
from pathlib import Path

import string_offset_request_base_runtime_float_integer_binary_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
EXPRESSIONS = (
    b'(~((!0.0) ? (-2.0) : (1/0)))',
    b'(~(-((float)(+(!INF)))))',
    b'(~(-' + prior.FLOAT_ONE + b'))',
    b'(~(' + prior.FLOAT_ONE + b' + 2.0))',
)
NAMES = (
    'string-offset-request-base-runtime-float-negative-two-bitnot-leading-key',
    'string-offset-request-base-runtime-float-negative-zero-bitnot-negative-key',
    'string-offset-marked-request-base-runtime-float-negative-one-bitnot-key-throw',
    'string-offset-request-base-runtime-float-three-bitnot-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), (_, _, old), name, expression in zip(prior.CASES.items(), prior.REPLACEMENTS, NAMES, EXPRESSIONS):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    CASES[name] = source.replace(old, expression)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
