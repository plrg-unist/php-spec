#!/usr/bin/env python3
"""Compare weak ordered bool/string reference Get, scalar preference and detach."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('bool_string_parentless_short_reference_get_hook')

if __name__ == '__main__':
    sources.main()
