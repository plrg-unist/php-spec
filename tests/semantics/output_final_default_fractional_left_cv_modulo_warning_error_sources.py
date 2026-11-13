#!/usr/bin/env python3
"""Fractional MOD prefixes in own left CVs precede quiet CONST-zero divisors."""
from pathlib import Path
import function_scope as scope
import output_final_default_fractional_cv_zero_modulo_warning_error_sources as prior

POSITIVE = prior.CASES['native-default-fractional-cv-zero-warning-modulo-integer-zero'].replace(
    b'$b = 0;', b"$b = '1.5x';").replace(b"return '1.5x' % $b;", b'return $b % 0;')
CASES = {'native-default-fractional-left-cv-warning-modulo-integer-zero': POSITIVE,
         'native-default-fractional-left-cv-warning-modulo-string-zero': POSITIVE.replace(
             b"'1.5x'", b"'-1.5x'").replace(b'return $b % 0;', b"return $b % '0';")}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-fractional-left-cv-modulo-warning-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
