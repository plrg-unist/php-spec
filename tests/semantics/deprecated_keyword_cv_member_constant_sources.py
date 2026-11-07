#!/usr/bin/env python3
"""Compare scoped-keyword constant reads with captured CV members."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_keyword_cv_member_constant')

if __name__ == '__main__':
    sources.main()
