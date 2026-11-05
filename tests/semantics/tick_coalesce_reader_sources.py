#!/usr/bin/env python3
"""Registered-handler quiet key reads resume callable-key coalesce assignment."""
from pathlib import Path

import tick_sources as ticks


SOURCE = Path(__file__).with_name('tick_coalesce_reader.php')
CASES = {'handler-callable-key-quiet-read': (SOURCE.read_bytes(), b'KTRT9ZWT')}


if __name__ == '__main__':
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(path.relative_to(ticks.ROOT)): ticks.sha(path) for path in [Path(__file__), SOURCE]}}
    ticks.CASES, ticks.CONTROLS = CASES, {}
    ticks.STATUSES = {name: 'normal' for name in CASES}
    ticks.EXITS = {name: 0 for name in CASES}
    ticks.main()
