#!/usr/bin/env python3
"""Independent repeated pending THROW with owning copied Generator returns."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_repeated_pending_owning_throw_review_cases.json')
source.PREFIX = 'generator-repeated-pending-owning-throw-review-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 100
source.PROCESS_SECONDS = 120

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
