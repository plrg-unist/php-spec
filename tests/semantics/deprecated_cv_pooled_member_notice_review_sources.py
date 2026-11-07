#!/usr/bin/env python3
"""Run class-CV reads with immutable members and protected callback reentry."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_cv_pooled_member_notice_review')

if __name__ == '__main__':
    sources.main()
