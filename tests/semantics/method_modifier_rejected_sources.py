#!/usr/bin/env python3
"""Method-target parser stops preserve only earlier encoding headers."""
from pathlib import Path
from rejected_encoding_sources import main

if __name__ == '__main__':
    main(Path(__file__).with_name('method_modifier_rejections'), (Path(__file__),))
