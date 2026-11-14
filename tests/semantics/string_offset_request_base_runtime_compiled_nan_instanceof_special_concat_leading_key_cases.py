"""Compiled NaN instanceof operands retain the four leading-key histories."""
from pathlib import Path

import string_offset_request_base_runtime_scalar_resolved_instanceof_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
EXPRESSIONS = (
    b'((int)((NAN instanceof stdClass) === (!INF)))',
    b'(~((int)((+NAN) instanceof \\stdClass)))',
    b'((int)((INF - INF) instanceof namespace\\MissingStringRead\\Target))',
    b'(~(((int)(((NAN ** 2) instanceof StringReadAlias) === (!INF))) + (1 + 1)))',
)
NAMES = (
    'string-offset-request-base-runtime-compiled-nan-instanceof-leading-key',
    'string-offset-request-base-runtime-compiled-nan-instanceof-negative-key',
    'string-offset-marked-request-base-runtime-compiled-nan-instanceof-key-throw',
    'string-offset-request-base-runtime-compiled-nan-instanceof-key-bounds',
)
CASES, OUTPUTS = {}, {}
for index, ((old_name, source), old, name, expression) in enumerate(zip(prior.CASES.items(), prior.EXPRESSIONS, NAMES, EXPRESSIONS)):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    prefix = b' use stdClass as StringReadAlias;' if index == 3 else b''
    source = b'<?php' + prefix + b'\n' + source.split(b'\n', 1)[1]
    CASES[name] = source.replace(old, expression)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
