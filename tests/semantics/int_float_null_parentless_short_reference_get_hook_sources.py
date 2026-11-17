#!/usr/bin/env python3
"""Compare weak ordered int/float/null reference Get and nullable initialization."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('int_float_null_parentless_short_reference_get_hook')

if __name__ == '__main__':
    sources.main()
