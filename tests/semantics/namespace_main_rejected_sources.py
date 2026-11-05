#!/usr/bin/env python3
"""Rejected main namespace units retain later encoding warnings."""
from pathlib import Path
from main_rejected_sources import main

if __name__ == '__main__':
    main(Path(__file__).with_name('namespace_main_rejections'), (Path(__file__),))
