#!/usr/bin/env python3
"""Compare shared global-CV property reads in an ordinary reader."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('property_reader_global_name_review_cases.json')
source.PREFIX = 'property-reader-global-name-review-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 120
source.PROCESS_SECONDS = 140
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
