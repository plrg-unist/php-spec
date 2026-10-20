#!/usr/bin/env python3
"""Original-source NULL-key warning snapshots and CV restoration."""
import incdec_warnings as runner
import array_literal_null_key_warning_cases as cases


if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
