#!/usr/bin/env python3
"""Rejected main methods preserve native early-modifier warning prefixes."""
from pathlib import Path
from main_rejected_sources import main

if __name__ == '__main__':
    main(Path(__file__).with_name('method_modifier_main_rejections'), (Path(__file__),))
