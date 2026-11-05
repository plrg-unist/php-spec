#!/usr/bin/env python3
"""Tick callback order across source Generator suspension and delegation."""
from pathlib import Path

import tick_sources as ticks


SOURCE = Path(__file__).with_name('tick_generator_resume.php')
CASES = {'yield-resume-order': (SOURCE.read_bytes(), b'S;A;T1;1;T2;B;T3;2;3;T4;C;T5;Z5;')}


if __name__ == '__main__':
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(path.relative_to(ticks.ROOT)): ticks.sha(path) for path in [Path(__file__), SOURCE]}}
    ticks.CASES, ticks.CONTROLS = CASES, {}
    ticks.STATUSES, ticks.EXITS = {'yield-resume-order': 'normal'}, {'yield-resume-order': 0}
    ticks.main()
