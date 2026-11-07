#!/usr/bin/env python3
"""Compare named public multi-constant Deprecated groups."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_multi_constant_group')

if __name__ == '__main__':
    sources.main()
