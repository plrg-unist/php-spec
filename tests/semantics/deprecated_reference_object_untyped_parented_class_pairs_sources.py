#!/usr/bin/env python3
"""Compare own untyped hook pairs over genuine plain source parents."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_parented_class_pairs')

if __name__ == '__main__':
    sources.main()
