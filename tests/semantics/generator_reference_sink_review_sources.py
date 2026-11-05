#!/usr/bin/env python3
"""Independent live-cell Generator delivery and cache identity controls."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_reference_sink_review_cases.json')
source.PREFIX = 'generator-reference-sink-review-source-'
source.IMPLEMENTATION = Path(__file__)
source.__doc__ = __doc__
source.MODEL_SECONDS = 100
source.PROCESS_SECONDS = 120

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
