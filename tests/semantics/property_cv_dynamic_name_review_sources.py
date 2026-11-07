#!/usr/bin/env python3
"""Compare delayed ordinary-CV property reads across computed names."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('property_cv_dynamic_name_review_cases.json')
source.PREFIX = 'property-cv-dynamic-name-review-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 120
source.PROCESS_SECONDS = 140
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
