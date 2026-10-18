#!/usr/bin/env python3
"""Native-first lossy CV list-key conversion and continuation agreements."""
import incdec_warnings as runner
import list_float_key_warning_cases as cases


if __name__ == '__main__':
    cases.CASES = {**cases.CASES, **cases.SOURCE_ONLY}
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
