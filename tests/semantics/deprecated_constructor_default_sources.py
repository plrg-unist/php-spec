#!/usr/bin/env python3
"""Compare original constructor-default sources under the checked profile."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_constructor_default')

if __name__ == '__main__':
    sources.main()
