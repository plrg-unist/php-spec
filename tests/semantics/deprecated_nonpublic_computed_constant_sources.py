#!/usr/bin/env python3
"""Compare source-authenticated private/protected computed constant access."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_nonpublic_computed_constant')

if __name__ == '__main__':
    sources.main()
