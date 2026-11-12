#!/usr/bin/env python3
"""Leading private CV division by its own initialized quiet scalar-zero CV."""
from pathlib import Path
import function_scope as scope
import output_final_default_division_warning_error_sources as prior

VALUES = {'integer': b'0', 'numeric-string': b"'0'"}
CASES = {'native-default-cv-zero-warning-division-' + name:
         prior.DIVISION.replace(b'        return $a / 0;', b'        $b = ' + value +
             b';\n        $c = ' + value + b';\n        return $a / $b;')
         for name, value in VALUES.items()}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-cv-zero-division-warning-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
