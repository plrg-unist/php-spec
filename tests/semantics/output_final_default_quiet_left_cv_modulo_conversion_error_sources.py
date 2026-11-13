#!/usr/bin/env python3
"""Own quiet left CVs precede noisy original CONST or own CV MOD divisors."""
from pathlib import Path
import function_scope as scope
import output_final_modulo_error_sources as prior
import output_final_default_right_modulo_conversion_error_sources as constants

VALUES = constants.VALUES
CASES = {}
for name, right in VALUES.items():
    CASES['native-default-quiet-left-cv-modulo-conversion-error-constant-' + name] = prior.MODULO.replace(
        b'return 1 % 0;', b'$left = 1;\n        return $left % ' + right + b';')
    CASES['native-default-quiet-left-cv-modulo-conversion-error-cv-' + name] = prior.MODULO.replace(
        b'return 1 % 0;', b'$left = 1;\n        $right = ' + right + b';\n        return $left % $right;')

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-quiet-left-cv-modulo-conversion-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
