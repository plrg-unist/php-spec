#!/usr/bin/env python3
"""Selected MOD handlers echo a literal and explicitly return integer zero."""
from pathlib import Path
import function_scope as scope
import output_final_selected_true_return_modulo_error_sources as prior

CASES = {}
for name, source in prior.CASES.items():
    assert source.count(b'selected_modulo_true_return') == 2
    assert source.count(b'return true;') + source.count(b'return TRUE;') == 1
    CASES[name.replace('selected-true-return', 'selected-zero-return')] = source.replace(
        b'selected_modulo_true_return', b'selected_modulo_zero_return').replace(
        b'return true;', b'return 0;').replace(b'return TRUE;', b'return 0;')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-zero-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
