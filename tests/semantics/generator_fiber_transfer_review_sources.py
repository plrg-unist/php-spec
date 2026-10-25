#!/usr/bin/env python3
"""Observe supplied Throwable injection into Generator bytecode parked in a Fiber."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_fiber_transfer_review_cases.json')
source.PREFIX = 'generator-fiber-transfer-review-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 100
source.PROCESS_SECONDS = 120
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
