#!/usr/bin/env python3
"""Selected MOD handlers return an own float cast of a raw integer literal."""
from pathlib import Path
import function_scope as scope
import output_final_selected_integer_cast_return_modulo_error_sources as prior

CASES = {}
for name, source in prior.CASES.items():
    assert source.count(b'selected_modulo_integer_cast_return') == 2
    assert source.count(b'return (int)') == 1
    CASES[name.replace('selected-integer-cast-return', 'selected-integer-float-cast-return')] = source.replace(
        b'selected_modulo_integer_cast_return', b'selected_modulo_integer_float_cast_return').replace(
        b'return (int)', b'return (float)')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-integer-float-cast-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
