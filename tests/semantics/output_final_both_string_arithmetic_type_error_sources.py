#!/usr/bin/env python3
"""Two nonnumeric strings retain native FINAL arithmetic TypeErrors."""
from pathlib import Path
import function_scope as scope
import output_final_left_arithmetic_type_error_sources as prior

ADD = prior.ADD.replace(b'$a + 1', b"$a + 'Y'")
SUBTRACT = ADD.replace(b"$a + 'Y'", b"$a - 'Y'")
MULTIPLY = ADD.replace(b"$a + 'Y'", b"$a * 'Y'")
DIVIDE = ADD.replace(b"$a + 'Y'", b"$a / 'Y'")
SWAPPED_MULTIPLY = MULTIPLY.replace(b"$a = 'X'", b"$a = 'Y'").replace(
    b"$a * 'Y'", b"'X' * $a")
NORMAL = prior.NORMAL
CASES = {'native-both-string-add-type-error': ADD,
         'native-both-string-subtract-type-error': SUBTRACT,
         'native-both-string-multiply-type-error': MULTIPLY,
         'native-both-string-divide-type-error': DIVIDE,
         'native-both-string-multiply-slot-order': SWAPPED_MULTIPLY,
         'native-both-string-arithmetic-normal': NORMAL}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-both-string-arithmetic-type-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
