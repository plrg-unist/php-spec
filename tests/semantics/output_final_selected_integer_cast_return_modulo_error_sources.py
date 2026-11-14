#!/usr/bin/env python3
"""Selected MOD handlers return an own int cast of a raw integer literal."""
from pathlib import Path
import function_scope as scope
import output_final_selected_positive_integer_return_modulo_error_sources as prior

CASES = {}
for name, source in prior.CASES.items():
    assert source.count(b'selected_modulo_positive_integer_return') == 2
    assert source.count(b'return +') == 1
    CASES[name.replace('selected-positive-integer-return', 'selected-integer-cast-return')] = source.replace(
        b'selected_modulo_positive_integer_return', b'selected_modulo_integer_cast_return').replace(
        b'return +', b'return (int)')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-integer-cast-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
