#!/usr/bin/env python3
"""Pinned native originals and checked-source array Iterator spread results."""
import array_iterator_unpack_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
