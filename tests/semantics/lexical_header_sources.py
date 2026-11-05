#!/usr/bin/env python3
"""Lexical failures retain only earlier completed foreign header reductions."""
from pathlib import Path
from rejected_encoding_sources import main

if __name__ == '__main__':
    main(Path(__file__).with_name('lexical_headers'), (Path(__file__),))
