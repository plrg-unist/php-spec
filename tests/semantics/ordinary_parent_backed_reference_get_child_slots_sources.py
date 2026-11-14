#!/usr/bin/env python3
"""Compare existing block reference getters and physical child slots."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('ordinary_parent_backed_reference_get_child_slots')

if __name__ == '__main__':
    sources.main()
