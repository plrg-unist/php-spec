"""Lexically resolved scalar-instanceof results retain leading-key histories."""
from pathlib import Path

import string_offset_request_base_runtime_scalar_qualified_instanceof_special_concat_leading_key_cases as prior

WATCHED = (*prior.WATCHED, str(Path(prior.__file__).resolve().relative_to(Path(__file__).resolve().parents[2])))
EXPRESSIONS = (
    b'((int)(((!0.0) instanceof StringReadAlias) === (!INF)))',
    b'(~((int)((!INF) instanceof StringReadPrefix\\Target)))',
    b"((int)((((!0.0) ? 'x' : (1/0))) instanceof namespace\\MissingStringRead\\Target))",
    b'(~(((int)(((+(!0.0)) instanceof stringreadprefix\\Target) === (!INF))) + (1 + 1)))',
)
PREFIXES = (b'use stdClass as StringReadAlias;', b'use Missing as StringReadPrefix;',
            b'', b'use Missing\\Deep as StringReadPrefix;')
NAMES = (
    'string-offset-request-base-runtime-scalar-resolved-instanceof-leading-key',
    'string-offset-request-base-runtime-scalar-resolved-instanceof-negative-key',
    'string-offset-marked-request-base-runtime-string-resolved-instanceof-key-throw',
    'string-offset-request-base-runtime-integer-resolved-instanceof-key-bounds',
)
CASES, OUTPUTS = {}, {}
for (old_name, source), old, name, expression, prefix in zip(prior.CASES.items(), prior.EXPRESSIONS, NAMES, EXPRESSIONS, PREFIXES):
    assert source.count(old) == 1
    assert expression.count(b'(') == expression.count(b')')
    source = source.replace(b'<?php\n', b'<?php ' + prefix + b'\n', 1) if prefix else source
    CASES[name] = source.replace(old, expression)
    OUTPUTS[name] = prior.OUTPUTS[old_name]
