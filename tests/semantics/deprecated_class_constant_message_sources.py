#!/usr/bin/env python3
"""Compare literal Deprecated message/since class-constant metadata."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_class_constant_message')

if __name__ == '__main__':
    sources.main()
