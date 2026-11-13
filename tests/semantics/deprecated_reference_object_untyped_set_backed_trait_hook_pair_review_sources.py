#!/usr/bin/env python3
"""Compare trait pairs backed through SET and shared outside ownership."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_set_backed_trait_hook_pair_review')

if __name__ == '__main__':
    sources.main()
