#!/usr/bin/env python3
"""Explicit array-to-string casts through the checked source recorder."""
import array_string_cast_cases as cases
import incdec_warnings as runner

runner.cases = cases

if __name__ == '__main__':
    raise SystemExit(0 if runner.main() else 1)
