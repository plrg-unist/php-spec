#!/usr/bin/env python3
"""Checked original-source agreements for concatenated quiet offset carriers."""
import string_offset_request_carriers_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
