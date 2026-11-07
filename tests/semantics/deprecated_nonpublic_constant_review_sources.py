#!/usr/bin/env python3
"""Run original nonpublic Deprecated constant visibility sources."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_nonpublic_constant_review')

if __name__ == '__main__':
    sources.main()
