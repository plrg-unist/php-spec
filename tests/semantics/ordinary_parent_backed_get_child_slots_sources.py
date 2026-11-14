#!/usr/bin/env python3
"""Compare lexical child slots and source-backed sole GET hooks."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('ordinary_parent_backed_get_child_slots')

if __name__ == '__main__':
    sources.main()
