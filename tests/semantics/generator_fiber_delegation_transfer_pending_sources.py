#!/usr/bin/env python3
"""Compare one retained delegation/Fiber source with a fixed 180s model budget.

The original 100s outcomes remain separate. Only captured native records are
accepted here; sources, profile, CPU/memory limits and step budget are unchanged.
"""
import argparse
from pathlib import Path

import fiber_static_api_sources as source

PENDING = {
    'generator-fiber-delegation-cached-next': 'generator_fiber_delegation_transfer_cases.json',
    'generator-fiber-delegation-cached-next-compact-output': 'generator_fiber_delegation_transfer_cases.json',
    'review-generator-fiber-delegation-transfer-handled': 'generator_fiber_delegation_transfer_review_cases.json',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=PENDING, action='append', required=True)
    parser.add_argument('--native-report', type=Path, action='append', required=True)
    args = parser.parse_args()
    if len(args.case) != 1:
        parser.error('exactly one pending --case is required')
    source.CASES = Path(__file__).with_name(PENDING[args.case[0]])
    source.PREFIX = 'generator-fiber-delegation-transfer-pending-source-'
    source.IMPLEMENTATION = Path(__file__)
    source.MODEL_SECONDS = 180
    source.PROCESS_SECONDS = 200
    source.__doc__ = __doc__
    return source.main()


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
