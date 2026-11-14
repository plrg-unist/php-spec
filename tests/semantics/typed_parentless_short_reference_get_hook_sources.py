#!/usr/bin/env python3
"""Compare canonical scalar/nullable short reference Get and real constraints."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('typed_parentless_short_reference_get_hook')

if __name__ == '__main__':
    sources.main()
