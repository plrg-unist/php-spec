#!/usr/bin/env python3
"""Compiler-only checks preserve later rejected-source header reductions."""
from pathlib import Path
from rejected_encoding_sources import main

if __name__ == '__main__':
    main(Path(__file__).with_name('static_rejections'), (Path(__file__),))
