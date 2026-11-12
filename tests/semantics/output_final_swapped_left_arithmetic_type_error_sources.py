#!/usr/bin/env python3
"""A BAD first physical MUL operand skips its leading lexical left."""
from pathlib import Path
import function_scope as scope
import output_final_default_arithmetic_warning_type_error_sources as prior

MULTIPLY = prior.MULTIPLY.replace(b"$a = '1.5x'", b"$a = 'X'").replace(
    b"$a * 'X'", b"'1.5x' * $a")
CASES = {'native-swapped-left-multiply-type-error': MULTIPLY}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-swapped-left-arithmetic-type-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
