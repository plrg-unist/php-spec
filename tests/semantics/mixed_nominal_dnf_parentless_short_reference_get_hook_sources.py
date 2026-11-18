#!/usr/bin/env python3
"""Compare quiet nominal DNF short-reference Get with builtin arms."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('mixed_nominal_dnf_parentless_short_reference_get_hook')

if __name__ == '__main__':
    sources.main()
