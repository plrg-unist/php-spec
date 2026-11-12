#!/usr/bin/env python3
"""FINAL zero errors retain quiet numeric and integer coercions separately."""
from pathlib import Path
import function_scope as scope
import output_final_division_error_sources as prior

DIVISION = prior.DIVISION.replace(b'        return 1 / 0;',
                                  b"        $a = true;\n        return $a / '0';")
MODULO = prior.DIVISION.replace(b'        return 1 / 0;',
                                b"        $a = '1.0';\n        $b = null;\n        return $a % $b;")
NORMAL = DIVISION.replace(b"$a / '0'", b"$a / '1'")
NOISY = MODULO.replace(b"$a = '1.0'", b"$a = '1.5'")
CATCH = MODULO.replace(b'        return $a % $b;',
                       b"        try { return $a % $b; } catch (DivisionByZeroError) { return 'H'; }")
OVERRIDE = MODULO.replace(b'        return $a % $b;',
                          b"        try { return $a % $b; } finally { return 'H'; }")
CASES = {'native-quiet-coercion-division': DIVISION,
         'native-quiet-coercion-modulo': MODULO,
         'native-quiet-coercion-normal': NORMAL}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-quiet-zero-coercion', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
