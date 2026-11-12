#!/usr/bin/env python3
"""FINAL modulo TypeErrors retain quiet left integer coercion and original types."""
from pathlib import Path
import function_scope as scope
import output_final_modulo_type_error_sources as prior

NULL = prior.INVALID.replace(b"        return 1 % 'X';",
                             b"        $a = null;\n        return $a % 'X';")
STRING = NULL.replace(b'$a = null', b"$a = '1.0'")
NORMAL = NULL.replace(b"$a % 'X'", b"$a % '2'")
NOISY = STRING.replace(b"$a = '1.0'", b"$a = '1.5'")
REFERENCE = NULL.replace(b"        return $a % 'X';",
                         b"        $r =& $a;\n        return $a % 'X';")
CASES = {'native-quiet-modulo-null-type-error': NULL,
         'native-quiet-modulo-string-type-error': STRING,
         'native-quiet-modulo-normal': NORMAL}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-quiet-modulo-type-coercion', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
