#!/usr/bin/env python3
"""Compare normal owning warning retval cleanup and copied Generator continuation."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_call_cleanup_return_cases.json')
source.PREFIX = 'generator-call-cleanup-return-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 600
source.PROCESS_SECONDS = 620
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
