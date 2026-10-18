#!/usr/bin/env python3
"""Owning copied returns in direct detached yield-from parents."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_owning_detached_return_cases.json')
source.PREFIX = 'generator-owning-detached-return-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 100
source.PROCESS_SECONDS = 120
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
