#!/usr/bin/env python3
"""Compare primitive union fields and nested shared/outside child owners."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_primitive_union_review')

if __name__ == '__main__':
    sources.main()
