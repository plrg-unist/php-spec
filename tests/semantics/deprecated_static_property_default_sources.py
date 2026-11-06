#!/usr/bin/env python3
"""Compare original static-default sources under the existing checked profile."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_static_property_default')

if __name__ == '__main__':
    sources.main()
