#!/usr/bin/env python3
"""Later fixed named Iterator reference sends with omitted earlier defaults."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('iterator_call_unpack_later_fixed_reference_cases.json')
source.PREFIX = 'iterator-call-unpack-later-fixed-reference-source-'
source.IMPLEMENTATION = Path(__file__)
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
