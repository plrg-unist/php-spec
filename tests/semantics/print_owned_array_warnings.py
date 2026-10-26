#!/usr/bin/env python3
"""Checked acquired-array print Warning sources and scalar control."""
import hashlib
from pathlib import Path

import incdec_warnings as runner
import print_owned_array_warning_cases as cases


def main():
    path = Path(__file__)
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    runner.cases = cases
    passed = runner.main()
    assert before == hashlib.sha256(path.read_bytes()).hexdigest()
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
