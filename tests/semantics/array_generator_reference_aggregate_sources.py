#!/usr/bin/env python3
"""Native and checked Aggregate-to-Generator reference cache source."""
import array_generator_reference_aggregate_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
