#!/usr/bin/env python3
"""Compare interface declaring caches, Closure aliases and typed reentry."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_interface_constant_review')

if __name__ == '__main__':
    sources.main()
