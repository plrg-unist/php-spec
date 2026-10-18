#!/usr/bin/env python3
"""Independent pending THROW with by-reference foreach wrapper and item aliases."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_pending_reference_foreach_throw_review_cases.json')
source.PREFIX = 'generator-pending-reference-foreach-throw-review-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 100
source.PROCESS_SECONDS = 120

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
