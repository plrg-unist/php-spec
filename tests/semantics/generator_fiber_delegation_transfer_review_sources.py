#!/usr/bin/env python3
"""Observe Throwable injection through a native Generator delegation link.

Default: accepted one-edge unhandled source. The two-edge handled reproducer
uses the separate fixed-budget entrypoint; its historical --case stays available.
"""
from pathlib import Path
import sys
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_fiber_delegation_transfer_review_cases.json')
source.PREFIX = 'generator-fiber-delegation-transfer-review-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 100
source.PROCESS_SECONDS = 120
source.__doc__ = __doc__

if __name__ == '__main__':
    if not any(arg == '--case' or arg.startswith('--case=') for arg in sys.argv[1:]):
        sys.argv += ['--case', 'review-generator-fiber-delegation-transfer-unhandled']
    raise SystemExit(0 if source.main() else 1)
