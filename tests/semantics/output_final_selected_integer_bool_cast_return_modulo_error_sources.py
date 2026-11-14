#!/usr/bin/env python3
"""Selected MOD handlers cast their own raw integer literals to Boolean."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior

CASES = {}
for (name, source), literal in zip(prior.CASES.items(),
                                 [b'0', b'0', b'7', b'9223372036854775807'], strict=True):
    assert source.count(b'selected_modulo_zero_return') == 2 and source.count(b'return 0;') == 1
    CASES[name.replace('selected-zero-return', 'selected-integer-bool-cast-return')] = source.replace(
        b'selected_modulo_zero_return', b'selected_modulo_integer_bool_cast_return').replace(
        b'return 0;', b'return (bool)' + literal + b';')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-integer-bool-cast-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
