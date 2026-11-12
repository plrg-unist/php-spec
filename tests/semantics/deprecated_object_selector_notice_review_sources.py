#!/usr/bin/env python3
"""Run temporary-object class selection with destructor notice reentry."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_object_selector_notice_review')

if __name__ == '__main__':
    sources.main()
