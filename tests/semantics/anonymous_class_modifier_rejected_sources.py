#!/usr/bin/env python3
"""Rejected anonymous-class modifiers stop before constructor/body headers."""
from pathlib import Path
from rejected_encoding_sources import main

if __name__ == '__main__':
    source = Path(__file__).with_name('anonymous_class_modifier_rejections')
    main(source, (Path(__file__), source / 'cases.json'))
