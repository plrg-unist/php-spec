#!/usr/bin/env python3
"""Ordered numeric bitwise assignment conversions through checked original sources."""
import bitassign_both_warning_cases as cases
import incdec_warnings as runner

runner.cases = cases

if __name__ == '__main__':
    raise SystemExit(0 if runner.main() else 1)
