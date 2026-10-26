#!/usr/bin/env python3
"""Native and checked source witnesses for reference-bearing Iterator caches."""
import array_traversable_reference_cache_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
