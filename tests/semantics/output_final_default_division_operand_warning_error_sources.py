#!/usr/bin/env python3
"""Default right-only and both-operand Warnings precede division-zero error."""
from pathlib import Path
import function_scope as scope
import output_final_default_division_warning_error_sources as constant
import output_final_default_cv_zero_division_warning_error_sources as cv

BOTH_CONSTANT = constant.DIVISION.replace(b'$a / 0', b"$a / '0x'")
BOTH_CV = cv.CASES['native-default-cv-zero-warning-division-numeric-string'].replace(
    b"$b = '0';", b"$b = '0x';").replace(b"$c = '0';", b"$c = '0x';")
CASES = {
    'native-default-division-operand-warning-right-constant': BOTH_CONSTANT.replace(b"$a = '1.5x';", b'$a = 1;'),
    'native-default-division-operand-warning-both-constant': BOTH_CONSTANT,
    'native-default-division-operand-warning-right-cv': BOTH_CV.replace(b"$a = '1.5x';", b"$a = '1.5';"),
    'native-default-division-operand-warning-both-cv': BOTH_CV,
}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-default-division-operand-warning-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
