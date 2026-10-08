#!/usr/bin/env python3
"""Ordinary Fiber API callable-array originals, serial native/model checks."""
from pathlib import Path
import fiber_static_api_sources as runner

if __name__ == '__main__':
    runner.CASES = Path(__file__).with_name('fiber_array_consumer_cases.json')
    runner.PREFIX = 'fiber-array-consumer-source-'
    runner.IMPLEMENTATION = Path(__file__)
    raise SystemExit(0 if runner.main() else 1)
