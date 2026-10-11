#!/usr/bin/env python3
"""Direct Iterator copied-object warnings after earlier extra named arguments."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fiber_static_api_sources as sources
sources.CASES = Path(__file__).with_name('iterator_call_unpack_object_extra_extra_cases.json')
sources.PREFIX = 'iterator-call-unpack-object-extra-extra-source-'
sources.IMPLEMENTATION = Path(__file__)
if __name__ == '__main__':
    raise SystemExit(0 if sources.main() else 1)
