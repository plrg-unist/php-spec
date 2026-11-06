#!/usr/bin/env python3
"""Compare receiver-free object-form static helpers during Generator reentry."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_object_static_helper_review_cases.json')
source.PREFIX = 'generator-object-static-helper-review-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 600
source.PROCESS_SECONDS = 620
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
