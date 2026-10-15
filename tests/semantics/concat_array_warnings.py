#!/usr/bin/env python3
"""Ordinary concatenation array warnings through the checked source recorder."""
import concat_array_warning_cases as cases
import incdec_warnings as runner

runner.cases = cases

if __name__ == '__main__':
    raise SystemExit(0 if runner.main() else 1)
