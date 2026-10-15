#!/usr/bin/env python3
"""Independent acquired-Iterator aliases, reference snapshots and COW cleanup."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_call_unpack_acquired_iterator_review_cases.json')
source.PREFIX = 'generator-call-unpack-acquired-iterator-review-source-'
source.IMPLEMENTATION = Path(__file__)
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
