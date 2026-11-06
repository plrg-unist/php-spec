#!/usr/bin/env python3
"""Compare shutdown registry ownership and direct-method default reentry."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_shutdown_method_default_review')

if __name__ == '__main__':
    sources.main()
