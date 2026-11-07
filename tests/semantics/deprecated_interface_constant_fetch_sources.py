#!/usr/bin/env python3
"""Compare selected Deprecated interface-constant FETCH originals."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_interface_constant_fetch')

if __name__ == '__main__':
    sources.main()
