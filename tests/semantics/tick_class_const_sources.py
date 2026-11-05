#!/usr/bin/env python3
"""Unticked class constants compile initializers without a main opcode."""
from pathlib import Path

import tick_sources as ticks


CASES = {
    'literal-class-constant-group-preserves-prior-main-tick': (b'''<?php
function t(){echo "T";}
register_tick_function("t");
declare(ticks=1);
class TickLiteral41 { public const A=1,B=2; }
1;
declare(ticks=2);
echo TickLiteral41::A;
echo TickLiteral41::B;
''', b'T12T'),
    'class-constant-closures-compile-in-group-order-without-main-opcode': (b'''<?php
function t(){echo "T";}
register_tick_function("t");
declare(ticks=1);
class TickOrder41 {
    public const FIRST=static function(){declare(ticks=2);echo "BAD";},
                 LAST=static function(){declare(ticks=1);echo "BAD";};
}
1;
echo "Z";
echo "W";
''', b'TZTWT'),
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
