#!/usr/bin/env python3
"""Deprecated VM calls, mixed warning phases and explicit API dependencies."""
import hashlib
from pathlib import Path

import deprecated_cases as cases
import deprecated_review_cases as reviewed
import incdec_warnings as runner


def main():
    watched = (Path(__file__), Path(reviewed.__file__))
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    cases.CASES = {**cases.CASES, **reviewed.CASES}
    cases.BOUNDARIES = reviewed.BOUNDARIES
    cases.BOUNDARY_STDOUT = reviewed.BOUNDARY_STDOUT
    runner.cases = cases
    passed = runner.main(model_timeout=150)
    assert before == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
