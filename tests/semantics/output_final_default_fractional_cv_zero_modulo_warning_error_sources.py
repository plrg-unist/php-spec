#!/usr/bin/env python3
"""Fractional MOD prefixes precede an own quiet-zero CV in FINAL methods."""
from pathlib import Path
import function_scope as scope
import output_final_default_fractional_modulo_warning_error_sources as prior

CASES = {
    'native-default-fractional-cv-zero-warning-modulo-integer-zero':
        prior.CASES['native-default-fractional-warning-modulo-positive'].replace(
            b"        return '1.5x' % 0;", b"        $b = 0;\n        return '1.5x' % $b;"),
    'native-default-fractional-cv-zero-warning-modulo-string-zero':
        prior.CASES['native-default-fractional-warning-modulo-negative'].replace(
            b"        return '-1.5x' % 0;", b"        $b = '0';\n        return '-1.5x' % $b;")}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-fractional-cv-zero-modulo-warning-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
