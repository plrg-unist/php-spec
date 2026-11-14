#!/usr/bin/env python3
"""Compare literal-name short reference Get cells and shared-child retirement."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('parentless_literal_short_reference_get_hook_review')

if __name__ == '__main__':
    sources.main()
