#!/usr/bin/env python3
"""Independent Generator-chain cache, COW, reference snapshot and child-lifetime cases."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_call_unpack_generator_delegation_review_cases.json')
source.PREFIX = 'generator-call-unpack-generator-delegation-review-source-'
source.IMPLEMENTATION = Path(__file__)
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
