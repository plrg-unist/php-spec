#!/usr/bin/env python3
"""Compare class/member CV snapshots through Deprecated constant notices."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_dual_cv_constant')

if __name__ == '__main__':
    sources.main()
