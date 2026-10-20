#!/usr/bin/env python3
"""Observe direct pending SEND snapshots with node-free copied child returns."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_unused_scalar_return_send_review_cases.json')
source.PREFIX = 'generator-unused-scalar-return-send-review-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 100
source.PROCESS_SECONDS = 120
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
