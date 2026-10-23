#!/usr/bin/env python3
"""Strict original observations for constant ARRAY values at NULL literal keys."""
import array_literal_null_key_constant_array_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
