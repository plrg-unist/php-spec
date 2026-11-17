#!/usr/bin/env python3
"""Compare strict ordered four-scalar reference Get and detached NULL aliases."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('int_float_bool_string_parentless_short_reference_get_hook_review')

if __name__ == '__main__':
    sources.main()
