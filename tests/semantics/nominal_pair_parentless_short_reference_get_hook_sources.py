#!/usr/bin/env python3
"""Original quiet nominal-pair short-reference Get comparisons."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('nominal_pair_parentless_short_reference_get_hook')

if __name__ == '__main__':
    sources.main()
