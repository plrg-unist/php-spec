#!/usr/bin/env python3
"""Checked bitwise NOT capture, negative-float truncation and false fallback."""
import hashlib
from pathlib import Path

import bitnot_warning_review_cases as cases
import incdec_warnings as runner


def main():
    wrapper = Path(__file__)
    before = hashlib.sha256(wrapper.read_bytes()).hexdigest()
    runner.cases = cases
    passed = runner.main()
    assert before == hashlib.sha256(wrapper.read_bytes()).hexdigest()
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
