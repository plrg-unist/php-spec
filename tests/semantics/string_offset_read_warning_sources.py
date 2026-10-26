#!/usr/bin/env python3
"""Original-source native preparation for string R-offset Warning callbacks."""
import string_offset_read_warning_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
