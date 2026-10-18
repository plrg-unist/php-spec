#!/usr/bin/env python3
"""Pending THROW with a used-yield input inside one by-reference array foreach."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_pending_buffered_reference_foreach_throw_cases.json')
source.PREFIX = 'generator-pending-buffered-reference-foreach-throw-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 100
source.PROCESS_SECONDS = 120
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
