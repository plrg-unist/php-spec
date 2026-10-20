#!/usr/bin/env python3
"""Original-source typed outer-array reference callback witnesses."""
import incdec_warnings as runner
import array_literal_float_typed_array_ref_cases as cases


if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
