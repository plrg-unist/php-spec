#!/usr/bin/env python3
"""Compare strict FLOAT/BOOL/STRING returns, INT widening and owner detach."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('float_bool_string_parentless_short_reference_get_hook_review')

if __name__ == '__main__':
    sources.main()
