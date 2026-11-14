"""Emitted arithmetic NaN instanceof operands retain leading-key histories."""
from pathlib import Path

import string_offset_request_base_runtime_compiled_nan_instanceof_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
NANS = (b'(((float)(!INF))*INF)', b'(((float)(!INF))-NAN)',
        b'(((float)(!0.0))/NAN)', b'(((float)(!INF))+NAN)')
EXPRESSIONS = (
    b'((int)((' + NANS[0] + b' instanceof stdClass) === (!INF)))',
    b'(~((int)(' + NANS[1] + b' instanceof \\stdClass)))',
    b'((int)(' + NANS[2] + b' instanceof namespace\\MissingStringRead\\Target))',
    b'(~(((int)(' + NANS[3] + b' instanceof StringReadAlias)) + (1 + 2)))',
)
NAMES = (
    'string-offset-request-base-runtime-arithmetic-nan-instanceof-leading-key',
    'string-offset-request-base-runtime-arithmetic-nan-instanceof-negative-key',
    'string-offset-marked-request-base-runtime-arithmetic-nan-instanceof-key-throw',
    'string-offset-request-base-runtime-arithmetic-nan-instanceof-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), old, name, expression in zip(prior.CASES.items(), prior.EXPRESSIONS, NAMES, EXPRESSIONS):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    CASES[name] = source.replace(old, expression)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
