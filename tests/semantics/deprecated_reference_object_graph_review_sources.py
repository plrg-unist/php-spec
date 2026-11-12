#!/usr/bin/env python3
"""Run nested selector field cleanup after a supplied deep-child exception."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_graph_review')

if __name__ == '__main__':
    sources.main()
