#!/usr/bin/env python3
"""Compare reference-object declared-child cleanup before member evaluation."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_property')

if __name__ == '__main__':
    sources.main()
