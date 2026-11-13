#!/usr/bin/env python3
"""Compare own untyped hook pairs over same-name plain parent properties."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_same_name_parent_class_pairs')

if __name__ == '__main__':
    sources.main()
