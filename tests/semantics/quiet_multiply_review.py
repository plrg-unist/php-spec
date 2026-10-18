#!/usr/bin/env python3
"""Independent quiet MUL physical rank and copied-type originals."""
import hashlib
from pathlib import Path
import quiet_multiply_review_cases as cases
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
