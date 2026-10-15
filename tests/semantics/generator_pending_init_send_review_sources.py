#!/usr/bin/env python3
"""Independent pending-initialization sends and argument-cleanup lifetimes."""
from pathlib import Path
import fiber_static_api_sources as source

source.CASES = Path(__file__).with_name('generator_pending_init_send_review_cases.json')
source.PREFIX = 'generator-pending-init-send-review-source-'
source.IMPLEMENTATION = Path(__file__)

if __name__ == '__main__':
    raise SystemExit(0 if source.main() else 1)
