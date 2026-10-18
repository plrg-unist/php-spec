#!/usr/bin/env python3
"""Strict original-source comparisons for reference-element retargeting."""
import incdec_warnings as runner
import array_literal_float_ref_key_warning_review_cases as cases

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
