#!/usr/bin/env python3
"""Compare inherited typed non-NUL request strings with shared and outside child edges."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_typed_string_review')

if __name__ == '__main__':
    sources.main()
