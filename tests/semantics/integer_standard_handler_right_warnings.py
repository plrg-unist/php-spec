#!/usr/bin/env python3
"""Checked standard-handler RIGHT objects through ordinary integer warnings."""
import hashlib
from pathlib import Path

import integer_standard_handler_right_warning_cases as cases
import incdec_warnings as runner


def main():
    path = Path(__file__)
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    runner.cases = cases
    passed = runner.main(model_timeout=150)
    assert before == hashlib.sha256(path.read_bytes()).hexdigest()
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
