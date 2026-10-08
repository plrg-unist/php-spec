#!/usr/bin/env python3
"""Bound Fiber start captures with exact native/model observations."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('fiber_start_capture_cases.json')
source.PREFIX = 'fiber-start-capture-source-'
source.__file__ = __file__
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
