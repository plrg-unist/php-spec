#!/usr/bin/env python3
"""Literal optional integer tails preserve supplied value/reference receives."""
import argparse
from pathlib import Path

import user_string

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    user_string.CASES = Path(__file__).with_name('optional_integer_tail_reception_cases.json')
    raise SystemExit(0 if user_string.run(args.match) else 1)
