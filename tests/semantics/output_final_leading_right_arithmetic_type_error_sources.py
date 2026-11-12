#!/usr/bin/env python3
"""An earlier invalid operand prevents a leading-number RHS warning in FINAL."""
from pathlib import Path
import function_scope as scope
import output_final_both_string_arithmetic_type_error_sources as prior

ADD = prior.ADD.replace(b"'Y'", b"'2x'")
SUBTRACT = prior.SUBTRACT.replace(b"'Y'", b"'2x'")
MULTIPLY = prior.MULTIPLY.replace(b"'Y'", b"'2x'")
DIVIDE = prior.DIVIDE.replace(b"'Y'", b"'2x'")
SWAPPED_MULTIPLY = prior.SWAPPED_MULTIPLY.replace(b"$a = 'Y'", b"$a = '2x'")
NORMAL = prior.NORMAL
CASES = {'native-leading-right-add-type-error': ADD,
         'native-leading-right-subtract-type-error': SUBTRACT,
         'native-leading-right-multiply-type-error': MULTIPLY,
         'native-leading-right-divide-type-error': DIVIDE,
         'native-leading-right-arithmetic-normal': NORMAL}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-leading-right-arithmetic-type-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
