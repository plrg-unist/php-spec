#!/usr/bin/env python3
"""Own noisy RHS CVs retain integer-conversion diagnostics before FINAL MOD errors."""
from pathlib import Path
import function_scope as scope
import output_final_modulo_error_sources as prior
import output_final_default_right_modulo_conversion_error_sources as constants

VALUES = constants.VALUES
CASES = {'native-default-right-cv-modulo-conversion-error-' + name:
         prior.MODULO.replace(b'return 1 % 0;', b'$right = ' + value + b';\n        return 1 % $right;')
         for name, value in VALUES.items()}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-right-cv-modulo-conversion-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
