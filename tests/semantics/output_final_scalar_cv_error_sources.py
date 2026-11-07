#!/usr/bin/env python3
"""FINAL conversion preserves generated errors from quiet private scalar CVs."""
from pathlib import Path
import function_scope as scope
import output_final_division_error_sources as prior

DIVISION = prior.DIVISION.replace(b'        return 1 / 0;',
                                  b'        $a = 0;\n        $b = 0;\n        return $a / $b;')
SHIFT = DIVISION.replace(b'$a = 0;', b'$a = 1;').replace(b'$b = 0;', b'$b = -1;').replace(b'$a / $b', b'$a << $b')
MULTIPLY = DIVISION.replace(b'$a = 0;', b'$a = 1;').replace(b'$b = 0;', b"$b = 'bad';").replace(b'$a / $b', b'$a * $b')
UNARY = DIVISION.replace(b'$a = 0;\n        $b = 0;', b"$a = 'bad';").replace(b'$a / $b', b'+$a')
BITNOT = DIVISION.replace(b'$a = 0;\n        $b = 0;', b'$a = true;').replace(b'$a / $b', b'~$a')
NORMAL = DIVISION.replace(b'$b = 0;', b'$b = 1;')
REFERENCE = DIVISION.replace(b'$b = 0;', b'$b = &$a;')
CASES = {'native-cv-division-zero': DIVISION,
         'native-cv-negative-shift': SHIFT,
         'native-cv-multiply-type-error': MULTIPLY,
         'native-cv-unary-type-error': UNARY,
         'native-cv-bitnot-type-error': BITNOT,
         'native-cv-division-normal': NORMAL}
CATCH = DIVISION.replace(b'        return $a / $b;',
                         b"        try { return $a / $b; } catch (DivisionByZeroError) { return 'H'; }")
OVERRIDE = DIVISION.replace(b'        return $a / $b;',
                            b"        try { return $a / $b; } finally { return 'H'; }")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-scalar-cv-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
