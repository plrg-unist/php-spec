#!/usr/bin/env python3
"""Compare nested declared object graphs with shared and retained children."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_graph')

if __name__ == '__main__':
    sources.main()
