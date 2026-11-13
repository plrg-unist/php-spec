#!/usr/bin/env python3
"""Compare backed modifier normalization and nested declaring-scope cleanup."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_modifiers_review')

if __name__ == '__main__':
    sources.main()
