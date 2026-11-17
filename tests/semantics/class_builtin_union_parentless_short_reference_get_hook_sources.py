#!/usr/bin/env python3
"""Original weak one-class/multiple-builtin short-reference Get comparisons."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('class_builtin_union_parentless_short_reference_get_hook')

if __name__ == '__main__':
    sources.main()
