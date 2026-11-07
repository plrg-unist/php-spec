#!/usr/bin/env python3
"""Compare scoped compiled members under existing method visibility."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_scoped_compiled_member_constant')

if __name__ == '__main__':
    sources.main()
