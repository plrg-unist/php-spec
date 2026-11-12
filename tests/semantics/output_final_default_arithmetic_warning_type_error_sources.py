#!/usr/bin/env python3
"""Default arithmetic Warnings precede native FINAL right-conversion TypeErrors."""
from pathlib import Path
import function_scope as scope
import output_final_quiet_arithmetic_type_coercion_sources as prior

SUBTRACT = prior.NOISY
ADD = SUBTRACT.replace(b"$a - 'X'", b"$a + 'X'")
MULTIPLY = SUBTRACT.replace(b"$a - 'X'", b"$a * 'X'")
DIVIDE = SUBTRACT.replace(b"$a - 'X'", b"$a / 'X'")
NORMAL = ADD.replace(b"$a + 'X'", b"$a + '2'")
CASES = {'native-default-warning-add-type-error': ADD,
         'native-default-warning-subtract-type-error': SUBTRACT,
         'native-default-warning-multiply-type-error': MULTIPLY,
         'native-default-warning-divide-type-error': DIVIDE,
         'native-default-warning-arithmetic-normal': NORMAL}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-arithmetic-warning-type-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
