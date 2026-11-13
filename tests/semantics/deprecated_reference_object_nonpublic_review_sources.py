#!/usr/bin/env python3
"""Compare nonpublic fields with declaring-scope reads and shared outside owners."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_nonpublic_review')

if __name__ == '__main__':
    sources.main()
