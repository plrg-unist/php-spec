#!/usr/bin/env python3
"""Foreach Aggregate dynamic original operand self comparison."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('foreach_source_compare_cases.json')
source.PREFIX = 'foreach-source-compare-source-'
source.IMPLEMENTATION = Path(__file__)
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
