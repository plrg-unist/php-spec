#!/usr/bin/env python3
"""Native-first mixed destructuring float-key protection checks."""
import incdec_warnings as runner
import list_float_ref_key_warning_cases as cases


if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
