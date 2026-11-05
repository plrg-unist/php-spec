#!/usr/bin/env python3
"""Compare literal nullsafe Generator API selection and reception."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_nullsafe_method_cases.json')
source.PREFIX = 'generator-nullsafe-method-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 240
source.PROCESS_SECONDS = 260
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
