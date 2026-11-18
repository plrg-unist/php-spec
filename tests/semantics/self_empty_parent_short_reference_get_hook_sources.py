#!/usr/bin/env python3
"""Compare own scoped-self reference Get over an empty named parent."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('self_empty_parent_short_reference_get_hook')

if __name__ == '__main__':
    sources.main()
