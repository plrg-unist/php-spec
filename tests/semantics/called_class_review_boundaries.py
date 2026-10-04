#!/usr/bin/env python3
"""Retain the unsupported discarded-warning producer beside called-class tests."""
from pathlib import Path

import closure_call_boundaries as boundaries

if __name__ == '__main__':
    boundaries.CASES = Path(__file__).with_suffix('.json')
    raise SystemExit(0 if boundaries.run() else 1)
