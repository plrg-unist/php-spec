#!/usr/bin/env python3
"""Native-first Aggregate-to-by-reference-Iterator spread witness."""
import array_iterator_byref_reference_aggregate_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
