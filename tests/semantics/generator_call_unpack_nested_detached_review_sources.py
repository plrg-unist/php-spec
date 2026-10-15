#!/usr/bin/env python3
"""Independent nested detached caches, real tails and intermediate cleanup."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_call_unpack_nested_detached_review_cases.json')
source.PREFIX = 'generator-call-unpack-nested-detached-review-source-'
source.IMPLEMENTATION = Path(__file__)

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
