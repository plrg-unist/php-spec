#!/usr/bin/env python3
"""Compare selected class-string constructor defaults and receiver cleanup."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_class_string_constructor_review')

if __name__ == '__main__':
    sources.main()
