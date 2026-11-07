#!/usr/bin/env python3
"""Run original Deprecated keyword-class/CV-member sources."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_keyword_member_cv_review')

if __name__ == '__main__':
    sources.main()
