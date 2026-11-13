#!/usr/bin/env python3
"""Compare nested backed getters through physical storage cleanup."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_backed_hook_review')

if __name__ == '__main__':
    sources.main()
