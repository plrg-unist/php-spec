#!/usr/bin/env python3
"""Native-first Aggregate-to-destructor Iterator spread witness."""
import array_iterator_byref_destructor_aggregate_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
