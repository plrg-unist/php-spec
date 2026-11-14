#!/usr/bin/env python3
"""Compare literal-string self-field short reference Get and alias lifetime."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('parentless_literal_short_reference_get_hook')

if __name__ == '__main__':
    sources.main()
