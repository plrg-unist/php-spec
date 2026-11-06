#!/usr/bin/env python3
"""Compare keyword constructor selection, factory cleanup and escaped exit."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_keyword_constructor_review')

if __name__ == '__main__':
    sources.main()
