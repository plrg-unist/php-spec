#!/usr/bin/env python3
"""Independent NaN bitwise-NOT original through the checked recorder."""
import hashlib
from pathlib import Path

import bitnot_nan_warning_review_cases as cases
import incdec_warnings as runner


def main():
    path = Path(__file__)
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    runner.cases = cases
    passed = runner.main()
    assert before == hashlib.sha256(path.read_bytes()).hexdigest()
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
