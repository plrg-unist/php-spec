#!/usr/bin/env python3
"""Main property-hook errors keep their native warning prefixes."""
from pathlib import Path
from main_rejected_sources import main

if __name__ == '__main__':
    source = Path(__file__).with_name('property_hook_static_main_rejections')
    main(source, (Path(__file__), source / 'cases.json'))
