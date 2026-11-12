#!/usr/bin/env python3
"""FINAL negative shifts retain quiet integer coercion of original operands."""
from pathlib import Path
import function_scope as scope
import output_final_shift_error_sources as prior

LEFT = prior.LEFT.replace(b'        return 1 << -1;',
                          b"        $a = null;\n        return $a << '-1';")
RIGHT = LEFT.replace(b'$a = null', b"$a = '1.0'").replace(b"$a << '-1'", b'$a >> -1.0')
NORMAL = LEFT.replace(b"$a << '-1'", b"$a << '0'")
NOISY = LEFT.replace(b"$a << '-1'", b"$a << '-1.5'")
REFERENCE = LEFT.replace(b"        return $a << '-1';",
                         b"        $r =& $a;\n        return $a << '-1';")
CASES = {'native-quiet-shift-left': LEFT,
         'native-quiet-shift-right': RIGHT,
         'native-quiet-shift-normal': NORMAL}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-quiet-shift-coercion', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
