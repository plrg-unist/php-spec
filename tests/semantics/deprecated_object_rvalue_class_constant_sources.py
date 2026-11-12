#!/usr/bin/env python3
"""Compare temporary ordinary-object class selection before Deprecated notice."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_object_rvalue_class_constant')

if __name__ == '__main__':
    sources.main()
