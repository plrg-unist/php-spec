#!/usr/bin/env python3
"""Compare CV-class capture through completed member effects and notices."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_cv_class_rvalue_member_constant')

if __name__ == '__main__':
    sources.main()
