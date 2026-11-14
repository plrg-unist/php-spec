#!/usr/bin/env python3
"""Selected MOD handlers return false and request ordered default diagnostics."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior

CASES = {}
for index, (name, source) in enumerate(prior.CASES.items()):
    assert source.count(b'selected_modulo_zero_return') == 2 and source.count(b'return 0;') == 1
    literal = b'false' if index < 2 else b'FALSE'
    CASES[name.replace('selected-zero-return', 'selected-false-return')] = source.replace(
        b'selected_modulo_zero_return', b'selected_modulo_false_return').replace(
        b'return 0;', b'return ' + literal + b';')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-false-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
