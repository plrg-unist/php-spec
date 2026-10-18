#!/usr/bin/env python3
"""Native-first NULL-CV list-key conversion and continuation agreements."""
import incdec_warnings as runner
import list_null_key_warning_cases as cases

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
