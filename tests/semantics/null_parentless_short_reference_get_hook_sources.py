#!/usr/bin/env python3
"""Compare canonical null reference Get, by-value initialization and real source detach."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('null_parentless_short_reference_get_hook')

if __name__ == '__main__':
    sources.main()
