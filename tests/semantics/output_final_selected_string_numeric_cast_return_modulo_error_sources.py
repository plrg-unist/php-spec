#!/usr/bin/env python3
"""Selected MOD handlers return quiet numeric casts of their own string literals."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior

CASES = {}
for (name, source), cast, literal, expected in zip(prior.CASES.items(),
        [b'int', b'int', b'float', b'float'],
        [b"''", b"'-4.75tail'", b"'x'", b"'0.125tail'"],
        [b'0', b'-4', b'0.0', b'0.125'], strict=True):
    assert source.count(b'selected_modulo_zero_return') == 2 and source.count(b'return 0;') == 1
    assert source.count(b"echo 'P';") == 1
    expression = b'(' + cast + b')' + literal
    witness = b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    CASES[name.replace('selected-zero-return', 'selected-string-numeric-cast-return')] = source.replace(
        b'selected_modulo_zero_return', b'selected_modulo_string_numeric_cast_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-string-numeric-cast-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
