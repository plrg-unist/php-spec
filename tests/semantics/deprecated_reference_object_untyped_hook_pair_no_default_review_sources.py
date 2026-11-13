#!/usr/bin/env python3
"""Compare omitted hook-pair defaults, native NULL and outside ownership."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_hook_pair_no_default_review')

if __name__ == '__main__':
    sources.main()
