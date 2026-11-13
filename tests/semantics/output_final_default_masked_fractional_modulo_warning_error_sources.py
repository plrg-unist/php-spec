#!/usr/bin/env python3
"""Reporting masks preserve fractional MOD conversion before FINAL zero Errors."""
from pathlib import Path
import function_scope as scope
import output_final_default_fractional_modulo_warning_error_sources as prior

MASKS = {'warning-only': (3, 'positive'),
         'deprecated-only': (8193, 'negative'),
         'neither': (1, 'positive')}
CASES = {'native-default-masked-fractional-warning-modulo-' + name:
         prior.CASES['native-default-fractional-warning-modulo-' + sign].replace(
             b'declare(strict_types=0);', b'declare(strict_types=0);\nerror_reporting(' + str(mask).encode() + b');')
         for name, (mask, sign) in MASKS.items()}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-masked-fractional-modulo-warning-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
