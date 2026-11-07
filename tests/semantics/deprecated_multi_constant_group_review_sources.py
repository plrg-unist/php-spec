#!/usr/bin/env python3
"""Run original public Deprecated multi-constant group sources."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).resolve().parent / 'deprecated_multi_constant_group_review'

if __name__ == '__main__':
    sources.main()
