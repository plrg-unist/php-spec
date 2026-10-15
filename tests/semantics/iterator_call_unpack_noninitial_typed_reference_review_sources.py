#!/usr/bin/env python3
"""Independent noninitial typed receives, repeated arrays and owning Error traces."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('iterator_call_unpack_noninitial_typed_reference_review_cases.json')
source.PREFIX = 'iterator-noninitial-typed-reference-review-source-'
source.IMPLEMENTATION = Path(__file__)
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
