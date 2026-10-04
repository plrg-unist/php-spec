#!/usr/bin/env python3
"""Default and variadic callable receives, warning fallback and boundaries."""
import argparse
from pathlib import Path

import user_string

CATALOGUE = Path(__file__).with_name('callable_receive_cases.json')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    user_string.CASES = CATALOGUE
    raise SystemExit(0 if user_string.run(args.match) else 1)
