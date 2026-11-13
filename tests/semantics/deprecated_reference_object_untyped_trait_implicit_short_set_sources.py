#!/usr/bin/env python3
"""Compare untyped explicit short SET DIRECT selector fields."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_trait_implicit_short_set')

if __name__ == '__main__':
    sources.main()
