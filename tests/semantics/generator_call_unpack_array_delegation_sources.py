#!/usr/bin/env python3
"""Ordinary Generator call unpack with delegated arrays and ordered cleanup."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_call_unpack_array_delegation_cases.json')
source.PREFIX = 'generator-array-unpack-source-'
source.IMPLEMENTATION = Path(__file__)
source.__doc__ = __doc__
source.MODEL_SECONDS = 100
source.PROCESS_SECONDS = 120

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
