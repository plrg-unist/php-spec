#!/usr/bin/env python3
"""Strict-SL captured-array return, COW and abrupt owner release."""
import argparse
from pathlib import Path

from undefined_spaceship_captured_array_review_cases import CASES
from undefined_spaceship_captured_array_review_protocol import PREFIX, checks
from undefined_spaceship_state import run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in (
        'peer-captured-left-returned-runtime',
        'peer-captured-right-assignment-default',
        'peer-captured-runtime-supplied-throw')}
    run(selected, checks, PREFIX, args.output)
