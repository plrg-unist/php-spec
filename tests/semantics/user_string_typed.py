#!/usr/bin/env python3
"""Original-source differential controls for weak user-object typed returns."""
import argparse
from pathlib import Path

import user_string

user_string.CASES = Path(__file__).with_name('user_string_typed_cases.json')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    raise SystemExit(0 if user_string.run(args.match) else 1)
