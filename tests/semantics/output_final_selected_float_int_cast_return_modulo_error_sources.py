#!/usr/bin/env python3
"""Selected MOD handlers return quiet int casts of raw float literals."""
from pathlib import Path
import function_scope as scope
import output_final_selected_integer_cast_return_modulo_error_sources as prior

CASES = {}
for (name, source), original, literal in zip(prior.CASES.items(),
        [b'1', b'7', b'0', b'9223372036854775807'],
        [b'1.5', b'5e-324', b'0.0', b'7.5'], strict=True):
    assert source.count(b'selected_modulo_integer_cast_return') == 2
    assert source.count(b'return (int)' + original + b';') == 1
    CASES[name.replace('selected-integer-cast-return', 'selected-float-int-cast-return')] = source.replace(
        b'selected_modulo_integer_cast_return', b'selected_modulo_float_int_cast_return').replace(
        b'return (int)' + original + b';', b'return (int)' + literal + b';')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-float-int-cast-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
