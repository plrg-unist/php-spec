#!/usr/bin/env python3
"""Strict original-source checks for autovivified writable key continuations."""
import incdec_warnings as runner
import list_float_write_autovivify_review_cases as cases

if __name__ == '__main__':
    runner.cases = cases
    raise SystemExit(0 if runner.main() else 1)
