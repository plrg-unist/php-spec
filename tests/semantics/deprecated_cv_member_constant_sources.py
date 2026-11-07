#!/usr/bin/env python3
"""Compare captured CV constant members and protected nested reads."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_cv_member_constant')

if __name__ == '__main__':
    sources.main()
