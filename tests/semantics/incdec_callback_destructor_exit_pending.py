#!/usr/bin/env python3
"""Original-source recorder for pending-Throwable callback-destructor exit."""
import hashlib
from pathlib import Path

import incdec_callback_destructor_exit_pending_cases as cases
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
