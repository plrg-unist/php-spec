#!/usr/bin/env python3
"""Fractional MOD prefixes and quiet zero divisors retain their own CVs."""
from pathlib import Path
import function_scope as scope
import output_final_default_fractional_left_cv_modulo_warning_error_sources as prior

POSITIVE = prior.POSITIVE.replace(b"$b = '1.5x';", b"$b = '1.5x';\n        $c = 0;").replace(
    b'return $b % 0;', b'return $b % $c;')
CASES = {'native-default-fractional-cv-pair-warning-modulo-integer-zero': POSITIVE,
         'native-default-fractional-cv-pair-warning-modulo-string-zero': POSITIVE.replace(
             b"'1.5x'", b"'-1.5x'").replace(b'$c = 0;', b"$c = '0';")}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-fractional-cv-pair-modulo-warning-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
