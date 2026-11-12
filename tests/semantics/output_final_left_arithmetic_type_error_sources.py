#!/usr/bin/env python3
"""Quiet nonnumeric left operands retain native FINAL arithmetic TypeErrors."""
from pathlib import Path
import function_scope as scope
import output_final_quiet_arithmetic_type_coercion_sources as prior

ADD = prior.ADD.replace(b"$a = '1.5'", b"$a = 'X'").replace(b"$a + 'X'", b'$a + 1')
SUBTRACT = ADD.replace(b'$a + 1', b'$a - null')
MULTIPLY = ADD.replace(b'$a + 1', b'$a * 1.5')
DIVIDE = ADD.replace(b'$a + 1', b'$a / true')
STRING_RIGHT = ADD.replace(b'$a + 1', b"$a + '2'")
SWAPPED_MULTIPLY = MULTIPLY.replace(b"$a = 'X'", b'$a = 1.5').replace(
    b'$a * 1.5', b"'X' * $a")
NORMAL = prior.NORMAL
CASES = {'native-left-string-add-int-type-error': ADD,
         'native-left-string-subtract-null-type-error': SUBTRACT,
         'native-left-string-multiply-float-type-error': MULTIPLY,
         'native-left-string-divide-bool-type-error': DIVIDE,
         'native-left-string-add-string-type-error': STRING_RIGHT,
         'native-left-string-multiply-slot-order': SWAPPED_MULTIPLY,
         'native-left-arithmetic-normal': NORMAL}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-left-arithmetic-type-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
