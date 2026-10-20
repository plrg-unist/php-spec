#!/usr/bin/env python3
"""Compare typed string-leaf originals against the pinned engine."""
import array_literal_float_typed_string_alias_leaf_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
