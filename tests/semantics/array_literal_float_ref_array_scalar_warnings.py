#!/usr/bin/env python3
"""Compare flat-array-to-scalar reference-key warning originals with pinned PHP."""
import array_literal_float_ref_array_scalar_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
