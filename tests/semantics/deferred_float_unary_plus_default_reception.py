#!/usr/bin/env python3
"""Deferred and folded unary plus retain their distinct signed-zero phases."""
import argparse
from pathlib import Path

import user_string

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    user_string.CASES = Path(__file__).with_name('deferred_float_unary_plus_default_reception_cases.json')
    raise SystemExit(0 if user_string.run(args.match) else 1)
