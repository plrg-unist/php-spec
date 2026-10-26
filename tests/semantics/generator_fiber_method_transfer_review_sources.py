#!/usr/bin/env python3
"""Compare ordinary Generator method receivers across Fiber transfer and cleanup."""
from pathlib import Path

import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_fiber_method_transfer_review_cases.json')
source.PREFIX = 'generator-fiber-method-transfer-review-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 180
source.PROCESS_SECONDS = 200
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
