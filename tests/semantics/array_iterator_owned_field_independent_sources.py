#!/usr/bin/env python3
"""Compare the independent owning-field singleton-leaf source with pinned PHP."""
import array_iterator_owned_field_independent_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
