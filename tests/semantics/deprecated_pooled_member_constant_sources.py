#!/usr/bin/env python3
"""Compare Deprecated constant notices with compiled string member operands."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_pooled_member_constant')

if __name__ == '__main__':
    sources.main()
