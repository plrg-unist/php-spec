#!/usr/bin/env python3
"""Compare short GET/block SET pairs through real getter expressions."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_pair_short_get')

if __name__ == '__main__':
    sources.main()
