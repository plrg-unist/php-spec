#!/usr/bin/env python3
"""Compare raw trait pairs backed only by their block SET hook."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_set_backed_trait_pairs')

if __name__ == '__main__':
    sources.main()
