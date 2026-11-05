#!/usr/bin/env python3
"""Compare ARRAY-packed copied Generator Closure::call from original bytes."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_call_array_pack_cases.json')
source.PREFIX = 'generator-call-array-pack-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 240
source.PROCESS_SECONDS = 260
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
