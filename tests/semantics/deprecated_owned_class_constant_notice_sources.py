#!/usr/bin/env python3
"""Compare attributed owning class-constant initializer originals."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_owned_class_constant_notice')

if __name__ == '__main__':
    sources.main()
