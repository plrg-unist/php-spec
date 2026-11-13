#!/usr/bin/env python3
"""Compare short SET backing with nested and outside physical owners."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_short_set_review')

if __name__ == '__main__':
    sources.main()
