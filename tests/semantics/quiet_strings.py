#!/usr/bin/env python3
"""Checked original compound assignments with quiet numeric-string RHS values."""
import quiet_string_cases as cases
import incdec_warnings as runner

runner.cases = cases

if __name__ == '__main__':
    raise SystemExit(0 if runner.main() else 1)
