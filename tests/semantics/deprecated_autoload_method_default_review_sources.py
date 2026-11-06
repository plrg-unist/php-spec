#!/usr/bin/env python3
"""Compare autoload default warnings, receiver retirement and cached rejection."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_autoload_method_default_review')

if __name__ == '__main__':
    sources.main()
