#!/usr/bin/env python3
"""A leading private CV warns before division by its original NULL operand."""
from pathlib import Path
import function_scope as scope
import output_final_default_division_warning_error_sources as prior

DIVISION = prior.DIVISION.replace(b'$a / 0', b'$a / null')
CASES = {'native-default-null-warning-division-error': DIVISION}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-null-division-warning-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
