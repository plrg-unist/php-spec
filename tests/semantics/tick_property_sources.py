#!/usr/bin/env python3
"""Plain property defaults compile in order without a main opcode or Tick."""
from pathlib import Path

import tick_sources as ticks


CASES = {
    'plain-property-default-groups-preserve-adjacency-and-initializer-order': (b'''<?php
function t(){echo "T";}
register_tick_function("t");
declare(ticks=1);
class TickLiteral42 { public $first=1,$second=2; }
1;
declare(ticks=2);
echo "P";
class TickPropertyOrder42 {
    public $first=static function(){declare(ticks=2);echo "BAD";},
           $last=static function(){declare(ticks=1);echo "BAD";};
}
1;
echo "Z";
echo "W";
''', b'TPZTWT'),
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
