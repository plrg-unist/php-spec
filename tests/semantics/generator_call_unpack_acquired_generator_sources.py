#!/usr/bin/env python3
"""Aggregate-acquired Generator data during by-value call unpack."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_call_unpack_acquired_generator_cases.json')
source.PREFIX = 'generator-acquired-generator-unpack-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 100
source.PROCESS_SECONDS = 120
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
