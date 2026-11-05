#!/usr/bin/env python3
"""Compare explicit native Generator API invoke wrapper phases and owners."""
from pathlib import Path
import fiber_static_api_sources as source
source.CASES = Path(__file__).with_name('generator_explicit_invoke_cases.json')
source.PREFIX = 'generator-explicit-invoke-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 400
source.PROCESS_SECONDS = 420
source.__doc__ = __doc__
if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
