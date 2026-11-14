#!/usr/bin/env python3
"""Selected MOD handlers echo a literal and execute an own bare return."""
from pathlib import Path
import function_scope as scope
import output_final_selected_explicit_null_modulo_error_sources as prior

CASES = {}
for name, source in prior.CASES.items():
    assert source.count(b'selected_modulo_explicit_null') == 2
    assert source.count(b'return null;') + source.count(b'return NULL;') == 1
    CASES[name.replace('selected-explicit-null', 'selected-bare-return')] = source.replace(
        b'selected_modulo_explicit_null', b'selected_modulo_bare_return').replace(
        b'return null;', b'return;').replace(b'return NULL;', b'return;')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-bare-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
