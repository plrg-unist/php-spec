#!/usr/bin/env python3
"""Plain trait use is unticked; enclosing DECLARE_CLASS still breaks adjacency."""
from pathlib import Path

import tick_sources as ticks


CASES = {
    'plain-trait-use-keeps-member-adjacency-before-the-class-emitter': (b'''<?php
function t(){echo "T";}
register_tick_function("t");
declare(ticks=1);
trait TickSource44 { public function unused(){declare(ticks=2);echo "BAD";} }
class TickUse44 { use TickSource44; }
declare(ticks=3);
echo "P";
echo "Z";
''', b'TPZT'),
}

CONTROLS = {
    'trait-adaptation-needs-its-own-tick-summary': (b'''<?php
function t(){echo "T";}
register_tick_function("t");
trait TickAliasSource44 { public function run(){return 7;} }
declare(ticks=1);
class TickAlias44 { use TickAliasSource44 { run as alias; } }
echo "Z";
''', b''),
}


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
