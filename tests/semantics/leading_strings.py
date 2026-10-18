#!/usr/bin/env python3
"""Checked original compounds with ordered float and numeric-string warnings."""
import leading_string_cases as cases
import incdec_warnings as runner

runner.cases = cases

if __name__ == '__main__':
    raise SystemExit(0 if runner.main() else 1)
