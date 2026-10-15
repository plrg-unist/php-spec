#!/usr/bin/env python3
"""Compound-shift fractional-RHS callbacks through checked original sources."""
import shiftassign_right_warning_cases as cases
import incdec_warnings as runner

runner.cases = cases

if __name__ == '__main__':
    raise SystemExit(0 if runner.main() else 1)
