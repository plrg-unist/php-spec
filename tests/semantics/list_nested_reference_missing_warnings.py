#!/usr/bin/env python3
"""Native-first checked nested mixed destructuring warning sources."""
import incdec_warnings as runner
import list_nested_reference_missing_warning_cases as cases


if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
