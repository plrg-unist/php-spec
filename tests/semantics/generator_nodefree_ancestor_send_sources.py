#!/usr/bin/env python3
"""Observe pending SEND at one ancestor above a node-free COMPLETE leaf."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_nodefree_ancestor_send_cases.json')
source.PREFIX = 'generator-nodefree-ancestor-send-source-'
source.IMPLEMENTATION = Path(__file__)
source.MODEL_SECONDS = 100
source.PROCESS_SECONDS = 120
source.__doc__ = __doc__

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
