#!/usr/bin/env python3
"""Run original Deprecated reads after effectful USER member calls."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_call_member_notice_review')

if __name__ == '__main__':
    sources.main()
