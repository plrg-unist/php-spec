#!/usr/bin/env python3
"""Plain global constant groups finish before their single trailing Tick."""
from pathlib import Path

import tick_sources as ticks


CASES = {
    'global-constant-group-and-single-bind-before-one-tick-each': (b'''<?php
$n=0;
function t(){
    global $n;
    $n=$n+1;
    echo "T";
    if($n===2){echo A;echo B;}
    if($n===3){echo C;}
}
register_tick_function("t");
declare(ticks=1);
const A=1,B=2;
const C=3;
echo "Z";
''', b'TT12T3ZT'),
}


def main(cases=CASES, producer=Path(__file__)):
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(path.relative_to(ticks.ROOT)): ticks.sha(path) for path in [Path(__file__), producer]}}
    ticks.CASES, ticks.CONTROLS = cases, {}
    ticks.STATUSES = {name: 'normal' for name in cases}
    ticks.EXITS = {name: 0 for name in cases}
    ticks.main()


if __name__ == '__main__':
    main()
