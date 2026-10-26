#!/usr/bin/env python3
"""Independent string-offset originals, with one explicit zero-credit boundary."""
import incdec_warnings as runner
import string_offset_read_warning_review_cases as cases

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
