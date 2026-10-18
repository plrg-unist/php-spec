#!/usr/bin/env python3
"""Strict independent array-literal reference-deficit source comparisons."""
import incdec_warnings as runner
import array_literal_float_ref_deficit_review_cases as cases

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
