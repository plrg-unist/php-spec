#!/usr/bin/env python3
"""Compare quiet stdClass payload identity through returned-value reference Notices."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('stdclass_reference_notice_cases.json')
source.PREFIX = 'stdclass-reference-notice-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 180
source.PROCESS_SECONDS = 195
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
