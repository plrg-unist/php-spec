#!/usr/bin/env python3
"""Compare the selected class-string constructor originals."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_class_string_constructor_default')

if __name__ == '__main__':
    sources.main()
