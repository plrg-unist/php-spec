#!/usr/bin/env python3
"""Native and checked Aggregate-to-by-reference-Generator source witness."""
import array_generator_byref_reference_aggregate_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
