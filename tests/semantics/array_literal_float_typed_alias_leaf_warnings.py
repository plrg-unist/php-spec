#!/usr/bin/env python3
"""Compare typed embedded-leaf originals against the pinned engine."""
import array_literal_float_typed_alias_leaf_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
