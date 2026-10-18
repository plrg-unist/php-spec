#!/usr/bin/env python3
"""Ancestor call-unpack through native Generators with an owning copied return."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_owning_chain_unpack_cases.json')
source.PREFIX = 'generator-owning-chain-unpack-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 100
source.PROCESS_SECONDS = 120
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
