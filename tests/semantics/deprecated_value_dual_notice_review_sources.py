#!/usr/bin/env python3
"""Run original Deprecated reads after completed class and member expressions."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_value_dual_notice_review')

if __name__ == '__main__':
    sources.main()
