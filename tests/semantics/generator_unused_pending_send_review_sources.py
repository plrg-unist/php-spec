#!/usr/bin/env python3
"""Unused pending SEND keeps a reference-row snapshot through argument cleanup and retires it before its receiver."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_unused_pending_send_review_cases.json')
source.PREFIX = 'generator-unused-pending-send-review-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 100
source.PROCESS_SECONDS = 120
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
