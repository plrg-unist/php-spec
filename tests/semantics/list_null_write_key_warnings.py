#!/usr/bin/env python3
"""Native-first NULL-CV list reference-key continuation comparisons."""
import incdec_warnings as runner
import list_null_write_key_warning_cases as cases

if __name__ == '__main__':
    cases.CASES = {**cases.CASES, **cases.SOURCE_ONLY}
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
