"""Quiet emitted weak equality consumes exact recursive NaN operands."""
from pathlib import Path

import string_offset_request_base_float_boolnot_special_concat_leading_key_cases as prior
import string_offset_request_base_runtime_null_left_nan_coalesce_instanceof_special_concat_leading_key_cases as nan

WATCHED = (*nan.WATCHED, 'tests/semantics/' + Path(nan.__file__).name,
           'tests/semantics/' + Path(prior.__file__).name)
NANS = nan.NANS
REPLACEMENTS = (
    ('string-offset-request-base-runtime-nan-equal-leading-key', b"(('' . (!0.0)) . 'x')", b'(+(' + NANS[0] + b' == (!0.0)))'),
    ('string-offset-request-base-runtime-reversed-nan-equal-negative-key', b"(('-' . (!(-0.0))) . 'x')", b'(~((int)(1.0 == ' + NANS[1] + b')))'),
    ('string-offset-marked-request-base-runtime-nan-integer-equal-key-throw', b"(('0' . (!INF)) . 'x')", b'((int)(' + NANS[2] + b' == 0))'),
    ('string-offset-request-base-runtime-nan-notequal-key-bounds', b"(('-4' . (!(1.0 + 2.0))) . 'x')", b'(~(((int)(' + NANS[3] + b' != NAN)) + (1 + 1)))'),
)
CASES, OUTPUTS = {}, {}
for (old_name, source), (name, old, expression) in zip(prior.CASES.items(), REPLACEMENTS):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    key = b'(( ' + expression + b" . false) . 'x')"
    CASES[name] = source.replace(old, key)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
