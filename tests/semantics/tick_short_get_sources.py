#!/usr/bin/env python3
"""Existing short GET bodies compile nested expressions with an implicit return."""
from pathlib import Path

import tick_sources as ticks


CASES = {
    'promoted-positive-frequency-short-getter': (b'''<?php
function t(){echo "T";}
register_tick_function("t");
declare(ticks=1);
class TickShortHook43 { public int $value { get => 7; } }
echo "Z";
''', b'TZT'),
    'unselected-short-getter-closure-compiles-without-a-reachable-return-tick': (b'''<?php
function t(){echo "T";}
register_tick_function("t");
declare(ticks=1);
class TickShortOrder51 {
    public int $value=7 {
        get => true ? $this->value : (static function(){
            declare(ticks=2);echo "BAD";return 0;
        })();
    }
}
$o=new TickShortOrder51;
echo $o->value;
echo "Z";echo "W";
''', b'T7TZWT'),
}
CONTROLS = {}


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
