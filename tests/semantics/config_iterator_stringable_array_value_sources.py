#!/usr/bin/env python3
"""Compare Iterator-copied array value rejection after Stringable option disposal."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('config_iterator_stringable_array_value_cases.json')
source.PREFIX = 'config-iterator-stringable-array-value-source-'
source.IMPLEMENTATION = Path(__file__)
source.__doc__ = __doc__
source.MODEL_SECONDS = 240
source.PROCESS_SECONDS = 260

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
