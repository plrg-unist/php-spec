#!/usr/bin/env python3
"""Main trait alias errors keep their native warning prefixes."""
from pathlib import Path
from main_rejected_sources import main

if __name__ == '__main__':
    source = Path(__file__).with_name('trait_alias_modifier_main_rejections')
    main(source, (Path(__file__), source / 'cases.json'))
