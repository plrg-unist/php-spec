#!/usr/bin/env python3
"""Compare ordinary-CV embedded-reference originals with the pinned engine."""
import array_literal_float_alias_leaf_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
