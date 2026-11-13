#!/usr/bin/env python3
"""Compare both-short untyped pairs with distinct GET and SET receipts."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_pair_both_short')

if __name__ == '__main__':
    sources.main()
