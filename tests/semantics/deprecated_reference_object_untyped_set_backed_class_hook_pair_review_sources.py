#!/usr/bin/env python3
"""Compare class SET-backed pairs and ordered child cleanup."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_set_backed_class_hook_pair_review')

if __name__ == '__main__':
    sources.main()
