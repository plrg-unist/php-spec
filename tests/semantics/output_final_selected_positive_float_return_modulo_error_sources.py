#!/usr/bin/env python3
"""Selected MOD handlers return an own unary-plus raw float literal."""
from pathlib import Path
import function_scope as scope
import output_final_selected_negative_float_return_modulo_error_sources as prior

CASES = {}
for name, source in prior.CASES.items():
    assert source.count(b'selected_modulo_negative_float_return') == 2
    assert source.count(b'return -') == 1
    CASES[name.replace('selected-negative-float-return', 'selected-positive-float-return')] = source.replace(
        b'selected_modulo_negative_float_return', b'selected_modulo_positive_float_return').replace(
        b'return -', b'return +')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-positive-float-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
