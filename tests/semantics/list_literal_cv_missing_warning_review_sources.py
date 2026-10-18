#!/usr/bin/env python3
"""Independent quiet-CV literal-root destructuring warning comparisons."""
import incdec_warnings as runner
import list_literal_cv_missing_warning_review_cases as cases


if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
