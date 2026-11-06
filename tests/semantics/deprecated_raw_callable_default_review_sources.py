#!/usr/bin/env python3
"""Compare selected raw CV method-callable defaults and source cleanup."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_raw_callable_default_review')

if __name__ == '__main__':
    sources.main()
