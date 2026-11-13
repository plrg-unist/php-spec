#!/usr/bin/env python3
"""Compare absent defaults and implicit NULL backing in public untyped pairs."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_pair_implicit_default')

if __name__ == '__main__':
    sources.main()
