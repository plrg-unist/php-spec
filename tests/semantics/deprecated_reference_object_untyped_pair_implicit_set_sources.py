#!/usr/bin/env python3
"""Compare public untyped GET/implicit block SET pairs in both source orders."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_pair_implicit_set')

if __name__ == '__main__':
    sources.main()
