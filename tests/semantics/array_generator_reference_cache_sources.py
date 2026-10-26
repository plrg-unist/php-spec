#!/usr/bin/env python3
"""Native and checked source witnesses for Generator reference cache arrays."""
import array_generator_reference_cache_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
