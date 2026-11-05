#!/usr/bin/env python3
"""Existing trait alias/precedence metadata does not recompile method bodies."""
from pathlib import Path

import tick_sources as ticks


CASES = {
    'promoted-plain-trait-alias-under-positive-ticks': (b'''<?php
function t(){echo "T";}
register_tick_function("t");
trait TickAliasSource44 { public function run(){return 7;} }
declare(ticks=1);
class TickAlias44 { use TickAliasSource44 { run as alias; } }
echo "Z";
''', b'TZT'),
    'trait-precedence-and-alias-keep-selected-physical-methods': (b'''<?php
function t(){echo "T";}
register_tick_function("t");
declare(ticks=1);
trait TickFirst45 { public function run(){declare(ticks=2);echo "A";return 1;} }
trait TickSecond45 { public function run(){declare(ticks=3);echo "B";return 2;} }
class TickSelect45 {
    use TickFirst45, TickSecond45 {
        TickFirst45::run insteadof TickSecond45;
        TickSecond45::run as alternate;
    }
}
$object=new TickSelect45;
echo $object->run();
echo $object->alternate();
echo "Z";
''', b'TTA1TB2ZT'),
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
