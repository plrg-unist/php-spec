#!/usr/bin/env python3
"""Compare actual untyped block SET parameters and DIRECT selector fields."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_set_explicit')

if __name__ == '__main__':
    sources.main()
