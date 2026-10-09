#!/usr/bin/env python3
"""IteratorAggregate yield-from acquisition and generic iterator data."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('yield_from_aggregate_cases.json')
source.PREFIX = 'yield-from-aggregate-source-'
source.IMPLEMENTATION = Path(__file__)
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
