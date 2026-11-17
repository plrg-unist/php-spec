#!/usr/bin/env python3
"""Compare literal-Boolean unions with actual array/object and alias payloads."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('literal_boolean_union_parentless_short_reference_get_hook')

if __name__ == '__main__':
    sources.main()
