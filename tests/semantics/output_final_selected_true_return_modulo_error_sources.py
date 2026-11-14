#!/usr/bin/env python3
"""Selected MOD handlers echo a literal and explicitly return true or TRUE."""
from pathlib import Path
import function_scope as scope
import output_final_selected_bare_return_modulo_error_sources as prior

CASES = {}
for index, (name, source) in enumerate(prior.CASES.items()):
    assert source.count(b'selected_modulo_bare_return') == 2 and source.count(b'return;') == 1
    literal = b'true' if index < 2 else b'TRUE'
    CASES[name.replace('selected-bare-return', 'selected-true-return')] = source.replace(
        b'selected_modulo_bare_return', b'selected_modulo_true_return').replace(
        b'return;', b'return ' + literal + b';')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-true-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
