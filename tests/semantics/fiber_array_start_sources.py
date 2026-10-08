#!/usr/bin/env python3
"""Ordinary Fiber array start originals, serial native/model checks."""
from pathlib import Path
import fiber_static_api_sources as runner

if __name__ == '__main__':
    runner.CASES = Path(__file__).with_name('fiber_array_start_cases.json')
    runner.PREFIX = 'fiber-array-start-source-'
    runner.IMPLEMENTATION = Path(__file__)
    raise SystemExit(0 if runner.main() else 1)
