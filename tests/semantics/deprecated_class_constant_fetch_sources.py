#!/usr/bin/env python3
"""Compare selected Deprecated class-constant FETCH originals."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_class_constant_fetch')

if __name__ == '__main__':
    sources.main()
