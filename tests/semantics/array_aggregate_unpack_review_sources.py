#!/usr/bin/env python3
"""Independent original Aggregate literal spread acquisition cases."""
import array_aggregate_unpack_review_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
