#!/usr/bin/env python3
"""Native-first checked quiet CV destructuring warning sources."""
import incdec_warnings as runner
import list_quiet_cv_missing_warning_cases as cases


if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
