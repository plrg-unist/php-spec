#!/usr/bin/env python3
"""Run direct-This class constants with normal receiver retention."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_this_owner_notice_review')

if __name__ == '__main__':
    sources.main()
