#!/usr/bin/env python3
"""Checked independent owning-handler local cleanup cancellation originals."""
import hashlib
from pathlib import Path

import incdec_warnings as runner
import incdec_callback_exit_cancellation_review_cases as cases


def main():
    wrapper = Path(__file__)
    before = hashlib.sha256(wrapper.read_bytes()).hexdigest()
    runner.cases = cases
    passed = runner.main()
    assert before == hashlib.sha256(wrapper.read_bytes()).hexdigest()
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
