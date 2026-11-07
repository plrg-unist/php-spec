#!/usr/bin/env python3
"""Compare Deprecated notices for immutable compiled class expressions."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_compiled_class_constant')

if __name__ == '__main__':
    sources.main()
