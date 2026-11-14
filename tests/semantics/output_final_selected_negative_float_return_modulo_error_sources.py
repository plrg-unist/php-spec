#!/usr/bin/env python3
"""Selected MOD handlers return an own unary-minus raw float literal."""
from pathlib import Path
import function_scope as scope
import output_final_selected_float_return_modulo_error_sources as prior

CASES = {}
for (name, source), literal in zip(prior.CASES.items(),
                                 [b'1.5', b'5e-324', b'0.0', b'1e309'], strict=True):
    assert source.count(b'selected_modulo_float_return') == 2
    assert source.count(b'return ' + literal + b';') == 1
    CASES[name.replace('selected-float-return', 'selected-negative-float-return')] = source.replace(
        b'selected_modulo_float_return', b'selected_modulo_negative_float_return').replace(
        b'return ' + literal + b';', b'return -' + literal + b';')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-negative-float-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
