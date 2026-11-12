#!/usr/bin/env python3
"""Ordered supplied integer reception across fixed positional formals."""
import argparse
from pathlib import Path

import user_string

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    user_string.CASES = Path(__file__).with_name('supplied_positional_integer_reception_cases.json')
    raise SystemExit(0 if user_string.run(args.match) else 1)
