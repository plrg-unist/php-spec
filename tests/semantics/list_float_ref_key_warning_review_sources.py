#!/usr/bin/env python3
"""Independent mixed-list float conversion and protected-table comparisons."""
import incdec_warnings as runner
import list_float_ref_key_warning_review_cases as cases


if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
