#!/usr/bin/env python3
"""Compare sole unbacked getters with appended slots and shared child cleanup."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('ordinary_parent_unbacked_get_child_slot_review')

if __name__ == '__main__':
    sources.main()
