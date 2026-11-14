#!/usr/bin/env python3
"""Deferred string producers preserve quiet negation before integer reception."""
import argparse
from pathlib import Path

import user_string

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    user_string.CASES = Path(__file__).with_name('produced_string_unary_minus_default_reception_cases.json')
    raise SystemExit(0 if user_string.run(args.match) else 1)
