#!/usr/bin/env python3
"""Native-first by-reference Iterator destructor spread witnesses."""
import array_iterator_byref_destructor_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
