#!/usr/bin/env python3
"""Compare repeated direct trait-pair uses, including lexical namespace aliases."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_repeated_trait_pairs')

if __name__ == '__main__':
    sources.main()
