#!/usr/bin/env python3
"""Rejected comma-list hooks retain only headers before the opening brace."""
from pathlib import Path
from rejected_encoding_sources import main

if __name__ == '__main__':
    source = Path(__file__).with_name('multiproperty_hook_rejections')
    main(source, (Path(__file__), source / 'cases.json'))
