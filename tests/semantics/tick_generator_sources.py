#!/usr/bin/env python3
"""Tick callback order across source Generator suspension and delegation."""
from pathlib import Path

import tick_sources as ticks


SOURCE = Path(__file__).with_name('tick_generator_resume.php')
CASES = {'yield-resume-order': (SOURCE.read_bytes(), b'S;A;T1;1;T2;B;T3;2;3;T4;C;T5;Z5;')}


def main(cases=CASES, producer=Path(__file__)):
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(path.relative_to(ticks.ROOT)): ticks.sha(path) for path in [Path(__file__), SOURCE, producer]}}
    ticks.CASES, ticks.CONTROLS = cases, {}
    ticks.STATUSES = {name: 'normal' for name in cases}
    ticks.EXITS = {name: 0 for name in cases}
    ticks.main()


if __name__ == '__main__':
    main()
