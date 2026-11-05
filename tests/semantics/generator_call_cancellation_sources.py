#!/usr/bin/env python3
"""Compare copied Generator Closure::call cancellation with PHP 8.5.10."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_call_cancellation_cases.json')
source.PREFIX = 'generator-call-cancellation-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 240
source.PROCESS_SECONDS = 260
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
