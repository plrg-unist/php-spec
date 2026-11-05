#!/usr/bin/env python3
"""Compare owning native Generator API captures and invocation."""
from pathlib import Path
import fiber_static_api_sources as source
source.CASES = Path(__file__).with_name('generator_api_capture_cases.json')
source.PREFIX = 'generator-api-capture-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 300
source.PROCESS_SECONDS = 320
source.__doc__ = __doc__
if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
