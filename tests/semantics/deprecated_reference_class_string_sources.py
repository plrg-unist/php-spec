#!/usr/bin/env python3
"""Compare defined local by-reference class-string selectors."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_class_string')

if __name__ == '__main__':
    sources.main()
