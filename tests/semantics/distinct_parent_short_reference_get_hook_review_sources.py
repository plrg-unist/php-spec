#!/usr/bin/env python3
"""Compare distinct parent fields with child short reference Get storage."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('distinct_parent_short_reference_get_hook_review')

if __name__ == '__main__':
    sources.main()
