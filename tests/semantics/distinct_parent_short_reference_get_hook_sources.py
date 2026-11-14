#!/usr/bin/env python3
"""Compare own short reference getters with a differently named parent field."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('distinct_parent_short_reference_get_hook')

if __name__ == '__main__':
    sources.main()
