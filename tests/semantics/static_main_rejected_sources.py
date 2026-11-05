#!/usr/bin/env python3
"""Rejected main parser errors precede class/try compiler validation."""
from pathlib import Path
from main_rejected_sources import main

if __name__ == '__main__':
    main(Path(__file__).with_name('static_main_rejections'), (Path(__file__),))
