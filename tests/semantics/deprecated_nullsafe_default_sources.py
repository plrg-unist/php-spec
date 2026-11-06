#!/usr/bin/env python3
"""Compare selected nullsafe method default originals."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_nullsafe_default')

if __name__ == '__main__':
    sources.main()
