#!/usr/bin/env python3
"""Compare namespace-relative self short-reference Get source originals."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('relative_self_parentless_short_reference_get_hook')

if __name__ == '__main__':
    sources.main()
