#!/usr/bin/env python3
"""Checked ordinary-source terminal string unset agreement."""
import string_offset_terminal_unset_cases as cases
import incdec_warnings as runner

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
