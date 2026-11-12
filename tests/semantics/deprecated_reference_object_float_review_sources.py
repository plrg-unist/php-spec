#!/usr/bin/env python3
"""Compare a nested NaN field with shared and externally retained child edges."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_float_review')

if __name__ == '__main__':
    sources.main()
