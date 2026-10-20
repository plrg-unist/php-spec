#!/usr/bin/env python3
"""Strict independent borrowed mixed-CV original-source comparisons."""
import incdec_warnings as runner
import array_literal_float_wrapped_mixed_cv_review_cases as cases

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
