#!/usr/bin/env python3
"""Compare direct This constant selection with inherited lexical scope."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_this_class_constant')

if __name__ == '__main__':
    sources.main()
