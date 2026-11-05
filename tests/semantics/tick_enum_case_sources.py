#!/usr/bin/env python3
"""Real EnumCase Tick prefixes precede the existing enum activation task."""
from pathlib import Path

import tick_sources as ticks


CASES = {
    'case-adjacency-retains-first-marker-frequency-before-enum-activation': (b'''<?php
function t(){echo "T";}
register_tick_function("t");
enum TickOrder40 {
    public function before(){declare(ticks=2);echo "BAD";}
    case A;
    public function between(){declare(ticks=1);echo "BAD";}
    case B;
}
declare(ticks=3);
echo "Z";
echo "W";
''', b'ZTW'),
    # Exact PHP bytes promoted from ATTR39's explicit dependency control.
    'prior-main-tick-suppresses-case-marker-without-suppressing-enum-emitter': (b'''<?php
function t(){echo "T";}
register_tick_function("t");
declare(ticks=1);
enum TickCases39 { case A; }
echo "Z";
''', b'TZT'),
}


def main(cases=CASES, producer=Path(__file__), controls=None):
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(path.relative_to(ticks.ROOT)): ticks.sha(path) for path in [Path(__file__), producer]}}
    ticks.CASES, ticks.CONTROLS = cases, controls or {}
    ticks.STATUSES = {name: 'normal' for name in cases}
    ticks.EXITS = {name: 0 for name in cases}
    ticks.main()


if __name__ == '__main__':
    main()
