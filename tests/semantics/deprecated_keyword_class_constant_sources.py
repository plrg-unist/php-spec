#!/usr/bin/env python3
"""Compare scoped keyword class-constant notice originals."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_keyword_class_constant')

if __name__ == '__main__':
    sources.main()
