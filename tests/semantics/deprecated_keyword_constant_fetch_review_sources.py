#!/usr/bin/env python3
"""Run original ordinary method-body keyword constant fetch sources."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_keyword_constant_fetch_review')

if __name__ == '__main__':
    sources.main()
