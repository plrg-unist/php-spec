#!/usr/bin/env python3
"""Compare inherited typed single-null fields with shared and outside child edges."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_typed_null_review')

if __name__ == '__main__':
    sources.main()
