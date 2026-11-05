#!/usr/bin/env python3
"""Constant-target parser errors preserve only earlier header reductions."""
from pathlib import Path
from rejected_encoding_sources import main

if __name__ == '__main__':
    main(Path(__file__).with_name('constant_modifier_rejections'), (Path(__file__),))
