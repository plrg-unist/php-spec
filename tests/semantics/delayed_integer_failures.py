#!/usr/bin/env python3
"""Checked originals for delayed integer-conversion failure and live type labels."""
import delayed_integer_failure_cases as cases
import incdec_warnings as runner

runner.cases = cases

if __name__ == '__main__':
    raise SystemExit(0 if runner.main() else 1)
