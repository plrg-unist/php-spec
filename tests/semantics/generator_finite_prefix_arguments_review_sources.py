#!/usr/bin/env python3
"""Compare finite Generator-CV prefixes at native Generator receivers."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_finite_prefix_arguments_review_cases.json')
source.PREFIX = 'generator-finite-prefix-arguments-review-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 600
source.PROCESS_SECONDS = 620
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
