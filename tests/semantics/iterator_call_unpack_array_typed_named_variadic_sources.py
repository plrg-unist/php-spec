#!/usr/bin/env python3
"""Direct Iterator nullable-array named variadic warning holds."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fiber_static_api_sources as sources
sources.CASES = Path(__file__).with_name('iterator_call_unpack_array_typed_named_variadic_cases.json')
sources.PREFIX = 'iterator-call-unpack-array-typed-named-variadic-source-'
sources.IMPLEMENTATION = Path(__file__)
if __name__ == '__main__':
    raise SystemExit(0 if sources.main() else 1)
