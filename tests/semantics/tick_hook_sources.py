#!/usr/bin/env python3
"""Block property hooks compile separate arrays in lexical member order."""
from pathlib import Path

import tick_sources as ticks


CASES = {
    'hook-bodies-preserve-main-adjacency-and-lexical-get-set-frequency': (b'''<?php
function t(){echo "T";}
register_tick_function("t");
declare(ticks=1);
class TickHookOrder43 {
    public int $value=7 {
        get { declare(ticks=2); echo "BAD"; return $this->value; }
        set { declare(ticks=1); echo "BAD"; $this->value=$value; }
    }
}
declare(ticks=1) { 1; }
echo "Z";
echo "W";
''', b'TZTWT'),
    'property-group-header-lines-follow-type-or-first-name': (b'''<?php
function t(){$trace=(new Exception)->getTrace();echo $trace[0]["line"];echo ";";}
register_tick_function("t");
interface TickHeaderI43 {}
class TickTyped43 implements TickHeaderI43 {
    public function unused(){declare(ticks=1);}
    public
    int
    $value=7;
}
class TickUntyped43 implements TickHeaderI43 {
    public
    $value=8;
}
echo "Z";
''', b'8;13;Z15;'),
}

CONTROLS = {}


def main(cases=CASES, producer=Path(__file__), controls=CONTROLS):
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(path.relative_to(ticks.ROOT)): ticks.sha(path) for path in [Path(__file__), producer]}}
    ticks.CASES, ticks.CONTROLS = cases, controls or {}
    ticks.STATUSES = {name: 'normal' for name in cases}
    ticks.EXITS = {name: 0 for name in cases}
    ticks.main()


if __name__ == '__main__':
    main()
