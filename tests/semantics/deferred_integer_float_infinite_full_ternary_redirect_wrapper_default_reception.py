#!/usr/bin/env python3
"""INT-left/FLOAT-right infinite predicates retain selected full-ternary tags and reception."""
import argparse
from pathlib import Path

import user_string

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    user_string.CASES = Path(__file__).with_name('deferred_integer_float_infinite_full_ternary_redirect_wrapper_default_reception_cases.json')
    raise SystemExit(0 if user_string.run(args.match) else 1)
