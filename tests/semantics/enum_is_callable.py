#!/usr/bin/env python3
"""Published generated enum methods queried by is_callable."""
import argparse
from pathlib import Path

import user_string

CATALOGUE = Path(__file__).with_name('enum_is_callable_cases.json')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    user_string.CASES = CATALOGUE
    raise SystemExit(0 if user_string.run(args.match) else 1)
