#!/usr/bin/env python3
"""Quiet integral-float numeric bitwise masks through checked original sources."""
import bitassign_quiet_float_cases as cases
import incdec_warnings as runner

runner.cases = cases

if __name__ == '__main__':
    raise SystemExit(0 if runner.main() else 1)
