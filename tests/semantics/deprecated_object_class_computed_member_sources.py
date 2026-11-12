#!/usr/bin/env python3
"""Compare ordinary-object class retirement before computed member effects."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_object_class_computed_member')

if __name__ == '__main__':
    sources.main()
