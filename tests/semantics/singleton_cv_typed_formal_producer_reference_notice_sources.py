#!/usr/bin/env python3
"""Compare singleton scalar/nullable receives and their later private Notice cells."""
from pathlib import Path

import fiber_static_api_sources as source
from scalar_return_producer_cv_reference_notice_run import recorded

source.CASES = Path(__file__).with_name('singleton_cv_typed_formal_producer_reference_notice_cases.json')
source.PREFIX = 'singleton-cv-typed-formal-producer-reference-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 180
source.PROCESS_SECONDS = 195
source.recorded = recorded
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
