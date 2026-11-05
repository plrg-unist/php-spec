#!/usr/bin/env python3
"""HALT_COMPILER emits no opcode but can own an adjacency-suppressed Tick."""
from pathlib import Path

import tick_sources as ticks


CASES = {
    'halt-compiler-emits-after-an-uncalled-method-enables-ticks': (b'''<?php
function t(){echo "T";}
register_tick_function("t");
class TickHalt48 { public function unused(){declare(ticks=1);} }
__halt_compiler();echo "BAD";
''', b'T'),
    'prior-tick-suppresses-halt-compiler-marker': (b'''<?php
function t(){echo "T";}
register_tick_function("t");
declare(ticks=1);
__halt_compiler();echo "BAD";
''', b'T'),
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
