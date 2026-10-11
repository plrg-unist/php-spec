#!/usr/bin/env python3
"""Direct Iterator copied-array warning and detached child-lifetime originals."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fiber_static_api_sources as sources
sources.CASES = Path(__file__).with_name('iterator_call_unpack_array_cases.json')
sources.PREFIX = 'iterator-call-unpack-array-source-'
sources.IMPLEMENTATION = Path(__file__)
if __name__ == '__main__':
    raise SystemExit(0 if sources.main() else 1)
