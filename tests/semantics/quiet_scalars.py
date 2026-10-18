#!/usr/bin/env python3
"""Checked original quiet bool/null conversions at compound-assignment resume."""
import quiet_scalar_cases as cases
import incdec_warnings as runner

runner.cases = cases

if __name__ == '__main__':
    raise SystemExit(0 if runner.main() else 1)
