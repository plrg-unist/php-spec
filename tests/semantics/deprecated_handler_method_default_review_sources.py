#!/usr/bin/env python3
"""Compare entered method handler ownership and rejected extra defaults."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_handler_method_default_review')

if __name__ == '__main__':
    sources.main()
