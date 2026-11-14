#!/usr/bin/env python3
"""Selected MOD handlers cast their own Boolean/null keywords to integer."""
from pathlib import Path
import function_scope as scope
import output_final_selected_constant_float_cast_return_modulo_error_sources as prior

CASES = {}
for name, source in prior.CASES.items():
    assert source.count(b'selected_modulo_constant_float_cast_return') == 2
    assert source.count(b'return (float)') == 1
    CASES[name.replace('selected-constant-float-cast-return', 'selected-constant-int-cast-return')] = source.replace(
        b'selected_modulo_constant_float_cast_return', b'selected_modulo_constant_int_cast_return').replace(
        b'return (float)', b'return (int)')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-constant-int-cast-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
