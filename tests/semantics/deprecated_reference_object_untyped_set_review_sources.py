#!/usr/bin/env python3
"""Compare nested untyped block SET defaults and physical storage."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_set_review')

if __name__ == '__main__':
    sources.main()
