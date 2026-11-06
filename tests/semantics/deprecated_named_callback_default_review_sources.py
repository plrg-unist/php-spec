#!/usr/bin/env python3
"""Compare selected named handlers, owning defaults and cache rejection."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_named_callback_default_review')

if __name__ == '__main__':
    sources.main()
