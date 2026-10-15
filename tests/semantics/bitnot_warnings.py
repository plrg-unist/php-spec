#!/usr/bin/env python3
"""Original bitwise NOT programs through the checked source recorder."""
import bitnot_warning_cases as cases
import incdec_warnings as runner

runner.cases = cases

if __name__ == '__main__':
    raise SystemExit(0 if runner.main() else 1)
