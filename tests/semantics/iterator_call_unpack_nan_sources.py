#!/usr/bin/env python3
"""Direct Iterator call-unpack valid NaN warning originals."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('iterator_call_unpack_nan_cases.json')
source.PREFIX = 'iterator-call-unpack-nan-source-'
source.IMPLEMENTATION = Path(__file__)
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
