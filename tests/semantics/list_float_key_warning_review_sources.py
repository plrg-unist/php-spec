#!/usr/bin/env python3
"""Independent lossy-float destructuring-key warning comparisons."""
import incdec_warnings as runner
import list_float_key_warning_review_cases as cases


if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
