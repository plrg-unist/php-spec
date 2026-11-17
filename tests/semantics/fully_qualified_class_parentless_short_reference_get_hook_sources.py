#!/usr/bin/env python3
"""Compare fully qualified class reference Get with live object owners and detach."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('fully_qualified_class_parentless_short_reference_get_hook')

if __name__ == '__main__':
    sources.main()
