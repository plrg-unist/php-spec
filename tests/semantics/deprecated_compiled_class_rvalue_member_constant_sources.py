#!/usr/bin/env python3
"""Compare delayed literal-class availability after completed member effects."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_compiled_class_rvalue_member_constant')

if __name__ == '__main__':
    sources.main()
