#!/usr/bin/env python3
"""Compare ordered array/null short reference headers and real constraints."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('union_array_parentless_short_reference_get_hook')

if __name__ == '__main__':
    sources.main()
