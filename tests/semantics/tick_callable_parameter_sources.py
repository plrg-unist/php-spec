#!/usr/bin/env python3
"""Ordinary callable defaults compile before bodies in their separate op arrays."""
from pathlib import Path

import tick_sources as ticks


CASES = {
    'closure-and-arrow-defaults-compile-before-bodies-in-source-order': (b'''<?php
function t(){echo "T";}
register_tick_function("t");
declare(ticks=1);
$c=function(
    $first=static function(){declare(ticks=3);echo "BADC1";},
    $second=static function(){declare(ticks=2);echo "BADC2";}
){echo "C";echo "D";return 1;};
declare(ticks=2);
echo "X";echo "Y";
echo $c(0,0);
$a=fn(
    $first=static function(){declare(ticks=3);echo "BADA1";},
    $second=static function(){declare(ticks=1);echo "BADA2";}
)=>print "A";
declare(ticks=1);
echo $a(0,0);
echo "Z";
''', b'TXTYCTD1TTA1TZT'),
}
CONTROLS = {
    'byref-closure-default-header-remains-a-dependency': (b'''<?php
$c=function &($cb=static function(){declare(ticks=1);}){return $cb;};
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
