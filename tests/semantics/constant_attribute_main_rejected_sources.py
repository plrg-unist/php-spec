#!/usr/bin/env python3
"""Main attributed constant lists preserve parser warning/error ordering."""
from pathlib import Path
from main_rejected_sources import main

if __name__ == '__main__':
    source = Path(__file__).with_name('constant_attribute_main_rejections')
    main(source, (Path(__file__), source / 'cases.json'))
