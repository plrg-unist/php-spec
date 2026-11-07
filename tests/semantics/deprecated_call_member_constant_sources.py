#!/usr/bin/env python3
"""Compare effects and captured results of user-function constant members."""
from pathlib import Path

import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_call_member_constant')

if __name__ == '__main__':
    sources.main()
