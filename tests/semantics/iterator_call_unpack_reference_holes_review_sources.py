#!/usr/bin/env python3
"""Independent fixed-slot reference holes, frozen keys and error ownership."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('iterator_call_unpack_reference_holes_review_cases.json')
source.PREFIX = 'iterator-reference-holes-review-source-'
source.IMPLEMENTATION = Path(__file__)
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
