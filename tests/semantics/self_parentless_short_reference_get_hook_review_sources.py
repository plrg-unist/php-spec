#!/usr/bin/env python3
"""Compare strict nullable and builtin-first self reference Get originals."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('self_parentless_short_reference_get_hook_review')

if __name__ == '__main__':
    sources.main()
