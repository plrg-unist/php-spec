#!/usr/bin/env python3
"""Selected MOD handlers return own nonzero signed-long integer literals."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior

CASES = {}
for (name, source), literal in zip(prior.CASES.items(),
                                 [b'1', b'9223372036854775807',
                                  b'0x4000_0000_0000_0001', b'0b101'], strict=True):
    assert source.count(b'selected_modulo_zero_return') == 2 and source.count(b'return 0;') == 1
    CASES[name.replace('selected-zero-return', 'selected-integer-return')] = source.replace(
        b'selected_modulo_zero_return', b'selected_modulo_integer_return').replace(
        b'return 0;', b'return ' + literal + b';')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-integer-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
