#!/usr/bin/env python3
"""Checked ordinary-source leading integer text string read agreements."""
import string_offset_leading_text_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
