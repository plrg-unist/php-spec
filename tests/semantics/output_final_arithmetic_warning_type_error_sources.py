#!/usr/bin/env python3
"""FINAL arithmetic TypeErrors resume after a returning numeric-Warning handler."""
from pathlib import Path
import function_scope as scope
import output_final_quiet_arithmetic_type_coercion_sources as prior

HANDLER = b"function eh($n,$m,$f,$l) { return true; }\nset_error_handler('eh');\n"


def returning(source, left):
    return source.replace(left, b"$a = '1.5x'").replace(
        b"ob_start('h'); echo 'A';", HANDLER + b"ob_start('h'); echo 'A';")


ADD = returning(prior.ADD, b"$a = '1.5'")
SUBTRACT = returning(prior.SUBTRACT, b'$a = null')
MULTIPLY = returning(prior.MULTIPLY, b'$a = 1.5')
DIVIDE = returning(prior.DIVIDE, b'$a = true')
NORMAL = ADD.replace(b"$a + 'X'", b"$a + '2'")
FALLBACK = ADD.replace(b'function eh($n,$m,$f,$l) { return true; }',
                       b'function eh($n,$m,$f,$l) { return false; }')
CASES = {'native-warning-add-type-error': ADD,
         'native-warning-subtract-type-error': SUBTRACT,
         'native-warning-multiply-type-error': MULTIPLY,
         'native-warning-divide-type-error': DIVIDE,
         'native-warning-arithmetic-normal': NORMAL,
         'native-warning-false-add-type-error': FALLBACK}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-arithmetic-warning-type-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
