#!/usr/bin/env python3
"""Independent constant-array NULL-key observations under the strict profile."""
import incdec_warnings as runner
import array_literal_null_key_constant_array_review_cases as cases

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
