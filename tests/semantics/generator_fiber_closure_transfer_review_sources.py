#!/usr/bin/env python3
"""Compare Closure callee transfer; --peer-budget-180 opts into fixed 180/200s caps."""
import argparse
from pathlib import Path
import sys

import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_fiber_closure_transfer_review_cases.json')
source.PREFIX = 'generator-fiber-closure-transfer-review-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 100
source.PROCESS_SECONDS = 120
source.__doc__ = __doc__

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--peer-budget-180', action='store_true')
    args, remaining = parser.parse_known_args()
    if args.peer_budget_180:
        source.MODEL_SECONDS = 180
        source.PROCESS_SECONDS = 200
    sys.argv[1:] = remaining
    raise SystemExit(0 if source.main() else 1)
