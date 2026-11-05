#!/usr/bin/env python3
"""Rejected eval scanner faults and unchanged file counterparts."""
from pathlib import Path
from rejected_encoding_sources import ROOT, main

if __name__ == '__main__':
    main(Path(__file__).with_name('unicode_rejections'),
         (Path(__file__), ROOT / 'native/php_file.c', ROOT / 'scripts/build-file-helper.sh'))
