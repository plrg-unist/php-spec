#!/usr/bin/env python3
"""Rejected property-hook checks preserve completed encoding headers."""
from pathlib import Path
from rejected_encoding_sources import main

if __name__ == '__main__':
    source = Path(__file__).with_name('property_hook_static_rejections')
    main(source, (Path(__file__), source / 'cases.json'))
