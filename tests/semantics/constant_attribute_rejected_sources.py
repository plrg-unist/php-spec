#!/usr/bin/env python3
"""Rejected attributed constant lists retain later completed headers."""
from pathlib import Path
from rejected_encoding_sources import main

if __name__ == '__main__':
    source = Path(__file__).with_name('constant_attribute_rejections')
    main(source, (Path(__file__), source / 'cases.json'))
