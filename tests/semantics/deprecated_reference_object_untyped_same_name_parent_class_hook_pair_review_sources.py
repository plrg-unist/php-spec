#!/usr/bin/env python3
"""Compare plain-parent overrides and child-slot cleanup with own hook pairs."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_same_name_parent_class_hook_pair_review')

if __name__ == '__main__':
    sources.main()
