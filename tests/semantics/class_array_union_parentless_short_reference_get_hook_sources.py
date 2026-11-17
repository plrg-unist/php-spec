#!/usr/bin/env python3
"""Original weak class/array short-reference Get source comparisons."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('class_array_union_parentless_short_reference_get_hook')

if __name__ == '__main__':
    sources.main()
