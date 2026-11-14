#!/usr/bin/env python3
"""Compare strict ordered nullable scalar getters, copies and released aliases."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('union_scalar_parentless_short_reference_get_hook_review')

if __name__ == '__main__':
    sources.main()
