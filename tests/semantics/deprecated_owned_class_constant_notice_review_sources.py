#!/usr/bin/env python3
"""Compare attributed class-constant owning initializer delivery."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_owned_class_constant_notice_review')

if __name__ == '__main__':
    sources.main()
