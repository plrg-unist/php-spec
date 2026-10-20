#!/usr/bin/env python3
"""Strict independent owning function-return literal-element comparisons."""
import incdec_warnings as runner
import array_literal_float_return_array_value_review_cases as cases

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
