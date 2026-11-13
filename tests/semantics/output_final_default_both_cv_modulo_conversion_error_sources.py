#!/usr/bin/env python3
"""Own noisy MOD CV pairs retain distinct and repeated private reads in FINAL."""
from pathlib import Path
import function_scope as scope
import output_final_modulo_error_sources as prior
import output_final_default_both_modulo_conversion_error_sources as constants

VALUES = constants.VALUES
CASES = {'native-default-both-cv-modulo-conversion-error-' + name:
         prior.MODULO.replace(b'return 1 % 0;', b'$left = ' + left + b';\n        $right = ' + right +
                              b';\n        return $left % $right;')
         for name, (left, right) in VALUES.items()}
CASES['native-default-both-cv-modulo-conversion-error-same-cv'] = prior.MODULO.replace(
    b'return 1 % 0;', b"$value = '0.5x';\n        return $value % $value;")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-both-cv-modulo-conversion-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
