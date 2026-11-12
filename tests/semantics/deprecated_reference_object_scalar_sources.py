#!/usr/bin/env python3
"""Compare singleton plain null, bool and int class-selector receiver fields."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_scalar')

if __name__ == '__main__':
    sources.main()
