"""Quiet literal-string integer operands retain real temporary key carriers."""
from pathlib import Path

import string_offset_request_base_runtime_literal_string_cast_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
ZERO, ONE = b'(+(!INF))', b'(+(!0.0))'
THREE = b'(' + ONE + b' + (' + ONE + b' + ' + ONE + b'))'


def selected(text):
    return b"((!0.0) ? '" + text + b"' : (1/0))"


EXPRESSIONS = (
    b'((' + selected(b'3.0') + b' | ' + ZERO + b') >> ' + selected(b'1e0') + b')',
    b'(~((+(' + selected(b'-1') + b' & ' + ZERO + b')) ^ ' + ZERO + b'))',
    b'(((' + ZERO + b") ? (1/0) : '-0.0') << " + ONE + b')',
    b'(~((+(' + selected(b'9223372036854775808') + b' % ' + selected(b'2') + b')) | ' + THREE + b'))',
)
NAMES = (
    'string-offset-request-base-runtime-literal-string-or-right-shift-leading-key',
    'string-offset-request-base-runtime-literal-string-and-xor-negative-key',
    'string-offset-marked-request-base-runtime-literal-string-left-shift-key-throw',
    'string-offset-request-base-runtime-literal-string-modulo-or-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), old, name, expression in zip(prior.CASES.items(), prior.EXPRESSIONS, NAMES, EXPRESSIONS):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    CASES[name] = source.replace(old, expression)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
