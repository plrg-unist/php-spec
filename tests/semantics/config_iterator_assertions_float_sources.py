#!/usr/bin/env python3
"""Compare copied float assertion values after option precision changes."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('config_iterator_assertions_float_cases.json')
source.PREFIX = 'config-iterator-assertions-float-source-'
source.IMPLEMENTATION = Path(__file__)
source.__doc__ = __doc__
source.MODEL_SECONDS = 600
source.PROCESS_SECONDS = 620

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
