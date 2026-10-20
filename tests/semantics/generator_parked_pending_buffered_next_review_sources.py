#!/usr/bin/env python3
"""Independent parked pending NEXT with one LIVE used-yield input; NULL adds no current copy."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_parked_pending_buffered_next_review_cases.json')
source.PREFIX = 'generator-parked-pending-buffered-next-review-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 100
source.PROCESS_SECONDS = 120
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
