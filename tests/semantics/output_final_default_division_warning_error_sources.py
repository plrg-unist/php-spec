#!/usr/bin/env python3
"""A leading private CV warns before its native FINAL division-by-zero error."""
from pathlib import Path
import function_scope as scope
import output_final_division_error_sources as prior

DIVISION = prior.DIVISION.replace(b'        return 1 / 0;',
    b"        $a = '1.5x';\n        return $a / 0;")
CASES = {'native-default-warning-division-error': DIVISION}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-division-warning-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
