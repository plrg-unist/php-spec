#!/usr/bin/env python3
"""Checked original-source agreements for ordinary interned quiet offsets."""
import string_offset_quiet_carriers_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
