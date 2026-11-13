#!/usr/bin/env python3
"""Compare implicit short SET pairs with real RHS and NULL/stored defaults."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_pair_short_set')

if __name__ == '__main__':
    sources.main()
