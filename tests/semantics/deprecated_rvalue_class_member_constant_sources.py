#!/usr/bin/env python3
"""Compare class-before-member effects and Deprecated constant selection."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_rvalue_class_member_constant')

if __name__ == '__main__':
    sources.main()
