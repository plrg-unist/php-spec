#!/usr/bin/env python3
"""Compare selected raw CV method-callable default originals."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_raw_callable_default')

if __name__ == '__main__':
    sources.main()
