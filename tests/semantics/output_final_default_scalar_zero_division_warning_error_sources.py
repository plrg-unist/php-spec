#!/usr/bin/env python3
"""Leading private CV division by original quiet scalar-zero constants."""
from pathlib import Path
import function_scope as scope
import output_final_default_null_division_warning_error_sources as prior

DIVISORS = {'false': b'false', 'float-positive': b'0.0', 'float-negative': b'-0.0',
            'string-integer': b"'0'", 'string-float-negative': b"'-0.0'"}
CASES = {'native-default-scalar-zero-warning-division-' + name:
         prior.DIVISION.replace(b'$a / null', b'$a / ' + divisor)
         for name, divisor in DIVISORS.items()}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-scalar-zero-division-warning-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
