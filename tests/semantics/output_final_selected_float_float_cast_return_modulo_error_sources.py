#!/usr/bin/env python3
"""Selected MOD handlers return an own float cast of a raw FLOAT literal."""
from pathlib import Path
import function_scope as scope
import output_final_selected_positive_float_return_modulo_error_sources as prior

CASES = {}
for name, source in prior.CASES.items():
    assert source.count(b'selected_modulo_positive_float_return') == 2
    assert source.count(b'return +') == 1
    CASES[name.replace('selected-positive-float-return', 'selected-float-float-cast-return')] = source.replace(
        b'selected_modulo_positive_float_return', b'selected_modulo_float_float_cast_return').replace(
        b'return +', b'return (float)')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-float-float-cast-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
