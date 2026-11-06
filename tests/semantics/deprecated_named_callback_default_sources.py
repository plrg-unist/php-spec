#!/usr/bin/env python3
"""Compare selected ordinary named callback default originals."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_named_callback_default')

if __name__ == '__main__':
    sources.main()
