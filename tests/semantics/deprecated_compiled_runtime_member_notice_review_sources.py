#!/usr/bin/env python3
"""Run original compiled class selectors with completed effectful members."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_compiled_runtime_member_notice_review')

if __name__ == '__main__':
    sources.main()
