#!/usr/bin/env python3
"""Rejected namespace structure preserves later grammar warning prefixes."""
from pathlib import Path
from rejected_encoding_sources import main

if __name__ == '__main__':
    main(Path(__file__).with_name('namespace_rejections'), (Path(__file__),))
