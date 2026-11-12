#!/usr/bin/env python3
"""Compare pending child exceptions across remaining physical selector fields."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_fields_review')

if __name__ == '__main__':
    sources.main()
