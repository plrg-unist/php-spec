#!/usr/bin/env python3
"""Main anonymous-class modifier errors preserve only earlier parser warnings."""
from pathlib import Path
from main_rejected_sources import main

if __name__ == '__main__':
    source = Path(__file__).with_name('anonymous_class_modifier_main_rejections')
    main(source, (Path(__file__), source / 'cases.json'))
