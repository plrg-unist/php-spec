#!/usr/bin/env python3
"""Compare completed rvalue member expressions before Deprecated notices."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_rvalue_member_constant')

if __name__ == '__main__':
    sources.main()
