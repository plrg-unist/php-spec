#!/usr/bin/env python3
"""Original scalar CONST left operands divide by their own leading-zero CV."""
from pathlib import Path
import function_scope as scope
import output_final_default_division_operand_warning_error_sources as prior

BASE = prior.BOTH_CV.replace(b"        $a = '1.5x';\n", b'')
VALUES = {'integer': b'1', 'numeric-string': b"'1.5'", 'leading-string': b"'1.5x'"}
CASES = {'native-default-constant-left-warning-division-' + name:
         BASE.replace(b'return $a / $b;', b'return ' + value + b' / $b;')
         for name, value in VALUES.items()}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-constant-left-division-warning-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
