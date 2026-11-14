#!/usr/bin/env python3
"""Compare inherited backing and appended slots for sole unbacked GET hooks."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('ordinary_parent_unbacked_get_child_slots')

if __name__ == '__main__':
    sources.main()
