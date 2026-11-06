#!/usr/bin/env python3
"""Compare CV-string method selection, inherited caches and receiver retirement."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_method_name_default_review')

if __name__ == '__main__':
    sources.main()
