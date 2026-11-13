#!/usr/bin/env python3
"""Compare automatic short-SET backing with unbacked block or short GET."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_automatic_short_set_trait_pairs')

if __name__ == '__main__':
    sources.main()
