"""Quiet primitive empty-CONCAT results retain existing interned headers."""
from pathlib import Path

import string_offset_request_base_runtime_empty_string_concat_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
FALSE, NULL = b'(!INF)', b'((!INF) ? true : null)'
ONE = b'(+(!0.0))'
THREE = b'(' + ONE + b' + (1 + 1))'
EXPRESSIONS = (
    b"((int)((" + FALSE + b" . (!0.0)) === '1'))",
    b"(~((int)('0' . " + NULL + b')))',
    b'((int)(' + FALSE + b' . ' + NULL + b'))',
    b'(~((int)((' + FALSE + b' . ' + THREE + b') . ' + FALSE + b')))',
)
NAMES = (
    'string-offset-request-base-runtime-primitive-empty-string-concat-leading-key',
    'string-offset-request-base-runtime-null-empty-string-concat-negative-key',
    'string-offset-marked-request-base-runtime-primitive-both-empty-string-concat-key-throw',
    'string-offset-request-base-runtime-primitive-nested-empty-string-concat-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), old, name, expression in zip(prior.CASES.items(), prior.EXPRESSIONS, NAMES, EXPRESSIONS):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    CASES[name] = source.replace(old, expression)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
