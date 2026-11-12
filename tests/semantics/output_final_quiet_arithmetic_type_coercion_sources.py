#!/usr/bin/env python3
"""FINAL arithmetic TypeErrors retain quiet left numeric coercion and original types."""
from pathlib import Path
import function_scope as scope
import output_final_modulo_type_error_sources as prior

ADD = prior.INVALID.replace(b"        return 1 % 'X';",
                            b"        $a = '1.5';\n        return $a + 'X';")
SUBTRACT = ADD.replace(b"$a = '1.5'", b'$a = null').replace(b"$a + 'X'", b"$a - 'X'")
MULTIPLY = ADD.replace(b"$a = '1.5'", b'$a = 1.5').replace(b"$a + 'X'", b"$a * 'X'")
DIVIDE = ADD.replace(b"$a = '1.5'", b'$a = true').replace(b"$a + 'X'", b"$a / 'X'")
NORMAL = ADD.replace(b"$a + 'X'", b"$a + '2'")
NOISY = SUBTRACT.replace(b'$a = null', b"$a = '1.5x'")
REFERENCE = SUBTRACT.replace(b"        return $a - 'X';",
                              b"        $r =& $a;\n        return $a - 'X';")
CASES = {'native-quiet-add-string-type-error': ADD,
         'native-quiet-subtract-null-type-error': SUBTRACT,
         'native-quiet-multiply-float-type-error': MULTIPLY,
         'native-quiet-divide-bool-type-error': DIVIDE,
         'native-quiet-arithmetic-normal': NORMAL}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-quiet-arithmetic-type-coercion', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
