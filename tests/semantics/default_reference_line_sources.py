#!/usr/bin/env python3
"""Compare default reference-send lines after a completed producer CV."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('default_reference_line_cases.json')
source.PREFIX = 'default-reference-line-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 120
source.PROCESS_SECONDS = 135
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
