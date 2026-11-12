#!/usr/bin/env python3
"""Original CONST operand pairs warn before zero division in an empty-CV method."""
from pathlib import Path
import function_scope as scope
import output_final_default_constant_left_division_warning_error_sources as prior

BASE = prior.BASE.replace(b"        $b = '0x';\n", b'').replace(b"        $c = '0x';\n", b'')
CASES = {'native-default-constant-pair-warning-division-' + name:
         BASE.replace(b'return $a / $b;', b'return ' + value + b" / '0x';")
         for name, value in prior.VALUES.items()}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-constant-pair-division-warning-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
