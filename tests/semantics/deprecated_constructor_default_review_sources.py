#!/usr/bin/env python3
"""Compare promoted constructor defaults and failed body-exit receivers."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_constructor_default_review')

if __name__ == '__main__':
    sources.main()
