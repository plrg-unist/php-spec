#!/usr/bin/env python3
"""Strict independent string-leaf literal-key conversion comparisons."""
import incdec_warnings as runner
import array_literal_float_string_leaf_review_cases as cases

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
