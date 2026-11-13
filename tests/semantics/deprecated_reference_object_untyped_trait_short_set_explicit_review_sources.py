#!/usr/bin/env python3
"""Compare direct-trait actual untyped short SET and outside ownership."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_trait_short_set_explicit_review')

if __name__ == '__main__':
    sources.main()
