#!/usr/bin/env python3
"""Noninitial fixed typed Iterator property-reference sends."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('iterator_call_unpack_noninitial_typed_reference_cases.json')
source.PREFIX = 'iterator-call-unpack-noninitial-typed-reference-source-'
source.IMPLEMENTATION = Path(__file__)
source.__doc__ = __doc__
source.MODEL_SECONDS = 100
source.PROCESS_SECONDS = 120

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
