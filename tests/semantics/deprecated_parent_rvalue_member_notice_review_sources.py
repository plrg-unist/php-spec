#!/usr/bin/env python3
"""Run original keyword/member reads retaining the normal instance receiver."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_parent_rvalue_member_notice_review')

if __name__ == '__main__':
    sources.main()
