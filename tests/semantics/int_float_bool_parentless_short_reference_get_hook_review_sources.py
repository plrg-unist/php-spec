#!/usr/bin/env python3
"""Compare strict quoted-field triple reference Get, failed coercions and detach."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('int_float_bool_parentless_short_reference_get_hook_review')

if __name__ == '__main__':
    sources.main()
