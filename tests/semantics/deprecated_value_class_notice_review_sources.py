#!/usr/bin/env python3
"""Run original Deprecated reads from completed string class selectors."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_value_class_notice_review')

if __name__ == '__main__':
    sources.main()
