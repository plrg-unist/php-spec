#!/usr/bin/env python3
"""Run original Deprecated reads through compiled class strings."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_pooled_class_notice_review')

if __name__ == '__main__':
    sources.main()
