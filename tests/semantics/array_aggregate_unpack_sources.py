#!/usr/bin/env python3
"""Pinned originals and checked-source IteratorAggregate array spread results."""
import array_aggregate_unpack_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
