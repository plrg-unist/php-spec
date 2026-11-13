#!/usr/bin/env python3
"""Compare directly imported actual untyped block SET and outside owners."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_trait_set_explicit_review')

if __name__ == '__main__':
    sources.main()
