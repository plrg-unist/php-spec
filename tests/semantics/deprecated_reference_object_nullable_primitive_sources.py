#!/usr/bin/env python3
"""Compare initialized plain DIRECT nullable primitive selector fields."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_nullable_primitive')

if __name__ == '__main__':
    sources.main()
