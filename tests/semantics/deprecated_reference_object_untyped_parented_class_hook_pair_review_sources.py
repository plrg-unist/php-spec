#!/usr/bin/env python3
"""Compare parented own-class pairs and inherited/unique/shared cleanup."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_parented_class_hook_pair_review')

if __name__ == '__main__':
    sources.main()
