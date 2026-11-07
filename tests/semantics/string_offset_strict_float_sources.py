#!/usr/bin/env python3
"""Checked ordinary-source strict float offset diagnostic agreement."""
import string_offset_strict_float_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
