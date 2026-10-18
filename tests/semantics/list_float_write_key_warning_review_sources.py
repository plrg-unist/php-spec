#!/usr/bin/env python3
"""Independent writable-key continuation source originals."""
import incdec_warnings as runner
import list_float_write_key_warning_review_cases as cases

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
