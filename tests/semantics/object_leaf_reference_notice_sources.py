#!/usr/bin/env python3
"""Compare ordinary DIRECT stdClass array leaves through reference-send Notices."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('object_leaf_reference_notice_cases.json')
source.PREFIX = 'object-leaf-reference-notice-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 180
source.PROCESS_SECONDS = 195
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
