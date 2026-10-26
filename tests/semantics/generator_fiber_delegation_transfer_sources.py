#!/usr/bin/env python3
"""Run accepted fresh transfer; cached NEXT remains an explicit pending case."""
from pathlib import Path
import sys
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_fiber_delegation_transfer_cases.json')
source.PREFIX = 'generator-fiber-delegation-transfer-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 100
source.PROCESS_SECONDS = 120
source.__doc__ = __doc__

if __name__ == '__main__':
    if not any(arg == '--case' or arg.startswith('--case=') for arg in sys.argv[1:]):
        sys.argv.extend(['--case', 'generator-fiber-delegation-fresh-current'])
    raise SystemExit(0 if source.main() else 1)
