#!/usr/bin/env python3
"""Stable Iterator-owned reference objects, detached warning holds and fresh cells."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fiber_static_api_sources as sources
sources.CASES = Path(__file__).with_name('iterator_call_unpack_reference_object_cases.json')
sources.PREFIX = 'iterator-call-unpack-reference-object-source-'
sources.IMPLEMENTATION = Path(__file__)
if __name__ == '__main__':
    raise SystemExit(0 if sources.main() else 1)
