#!/usr/bin/env python3
"""Named parameter defaults compile before the body without main-opcode effects."""
from pathlib import Path

import tick_sources as ticks


CASES = {
    'named-defaults-compile-left-to-right-before-body-preserving-main-adjacency': (b'''<?php
function t(){echo "T";}
register_tick_function("t");
declare(ticks=1);
function tickParameters49(
    $first=static function(){declare(ticks=3);echo "BAD1";},
    $second=static function(){declare(ticks=2);echo "BAD2";}
){echo "F";echo "G";}
declare(ticks=2);
echo "Z";echo "W";
tickParameters49(0,0);
echo "E";
''', b'TZWTFGTET'),
}
CONTROLS = {
    'byref-named-default-callable-remains-a-dependency': (b'''<?php
function &tickReference49($cb=static function(){declare(ticks=1);}){return $cb;}
echo "Z";
''', b''),
}


def main(cases=CASES, controls=CONTROLS, producer=Path(__file__)):
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(path.relative_to(ticks.ROOT)): ticks.sha(path) for path in [Path(__file__), producer]}}
    ticks.CASES, ticks.CONTROLS = cases, controls
    ticks.STATUSES = {name: 'normal' for name in cases}
    ticks.EXITS = {name: 0 for name in cases}
    ticks.main()


if __name__ == '__main__':
    main()
