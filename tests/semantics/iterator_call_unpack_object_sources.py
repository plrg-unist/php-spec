#!/usr/bin/env python3
"""Direct Iterator copied-object warning and pre-warning hold originals."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fiber_static_api_sources as sources
sources.CASES = Path(__file__).with_name('iterator_call_unpack_object_cases.json')
sources.PREFIX = 'iterator-call-unpack-object-source-'
sources.IMPLEMENTATION = Path(__file__)
if __name__ == '__main__':
    raise SystemExit(0 if sources.main() else 1)
