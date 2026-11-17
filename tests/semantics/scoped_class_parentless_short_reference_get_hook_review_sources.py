#!/usr/bin/env python3
"""Strict class Get names retain defining namespace/import context."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('scoped_class_parentless_short_reference_get_hook_review')

if __name__ == '__main__':
    sources.main()
