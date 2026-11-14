#!/usr/bin/env python3
"""Compare object short reference Get identity, constraints and receiver detach."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('object_parentless_short_reference_get_hook')

if __name__ == '__main__':
    sources.main()
