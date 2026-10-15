#!/usr/bin/env python3
"""Independent later raw arrays, repeated containers and fixed-key cleanup."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('iterator_call_unpack_noninitial_array_review_cases.json')
source.PREFIX = 'iterator-noninitial-array-review-source-'
source.IMPLEMENTATION = Path(__file__)
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
