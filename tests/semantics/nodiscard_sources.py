#!/usr/bin/env python3
"""NoDiscard declarations and warning phases through checked original sources."""
import hashlib
from pathlib import Path

import nodiscard_cases as cases
import nodiscard_review_cases as reviewed
import incdec_warnings as runner


def main():
    path = Path(__file__)
    watched = (path, Path(reviewed.__file__))
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    cases.CASES = {**cases.CASES, **reviewed.CASES}
    runner.cases = cases
    passed = runner.main(model_timeout=150)
    assert before == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
