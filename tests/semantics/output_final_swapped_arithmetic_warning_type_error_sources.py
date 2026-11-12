#!/usr/bin/env python3
"""Swapped default MUL warns before its native FINAL TypeError."""
from pathlib import Path
import function_scope as scope
import output_final_leading_right_arithmetic_type_error_sources as prior

MULTIPLY = prior.SWAPPED_MULTIPLY
CASES = {'native-swapped-warning-multiply-type-error': MULTIPLY}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-swapped-arithmetic-warning-type-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
