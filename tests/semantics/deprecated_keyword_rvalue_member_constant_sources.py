#!/usr/bin/env python3
"""Compare scoped-keyword constants after effectful member completion."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_keyword_rvalue_member_constant')

if __name__ == '__main__':
    sources.main()
