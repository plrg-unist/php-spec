#!/usr/bin/env python3
"""Run protected computed-constant access and caller COW observations."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_protected_computed_notice_review')

if __name__ == '__main__':
    sources.main()
