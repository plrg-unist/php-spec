#!/usr/bin/env python3
"""Foreach target compilation and callbacks follow value-before-key order."""
from pathlib import Path

import tick_sources as ticks


CASES = {
    'foreach-targets-compile-value-before-key-on-every-iteration': (b'''<?php
$keys=[];$values=[];
function t(){echo "T";}
register_tick_function("t");
declare(ticks=1){
    foreach([10,20] as
        $keys[(function(){declare(ticks=1);echo "K";return 0;})()] =>
        $values[(function(){declare(ticks=2);echo "V";return 0;})()]
    ){echo "B";}
    echo "Z";
}
echo $values[0];echo $keys[0];
''', b'VTTKTBTVTTKTBTTZT201'),
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
