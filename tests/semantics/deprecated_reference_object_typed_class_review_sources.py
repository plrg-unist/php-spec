#!/usr/bin/env python3
"""Compare typed nested object edges with subclass sharing and an outside owner."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_typed_class_review')

if __name__ == '__main__':
    sources.main()
