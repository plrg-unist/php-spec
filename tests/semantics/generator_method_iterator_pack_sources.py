#!/usr/bin/env python3
"""Compare direct native Generator API reception from initialized Iterator CVs."""
from pathlib import Path
import fiber_static_api_sources as source
source.CASES = Path(__file__).with_name('generator_method_iterator_pack_cases.json')
source.PREFIX = 'generator-method-iterator-pack-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 500
source.PROCESS_SECONDS = 520
source.__doc__ = __doc__
if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
