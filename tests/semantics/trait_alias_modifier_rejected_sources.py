#!/usr/bin/env python3
"""Rejected trait alias modifiers preserve only earlier encoding headers."""
from pathlib import Path
from rejected_encoding_sources import main

if __name__ == '__main__':
    source = Path(__file__).with_name('trait_alias_modifier_rejections')
    main(source, (Path(__file__), source / 'cases.json'))
