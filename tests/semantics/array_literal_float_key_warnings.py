#!/usr/bin/env python3
"""Native-first finite float array-literal key continuation comparisons."""
import incdec_warnings as runner
import array_literal_float_key_warning_cases as cases

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
