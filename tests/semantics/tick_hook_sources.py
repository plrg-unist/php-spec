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
}

CONTROLS = {
    'positive-frequency-short-hook-needs-synthetic-emitter-summary': (b'''<?php
function t(){echo "T";}
register_tick_function("t");
declare(ticks=1);
class TickShortHook43 { public int $value { get => 7; } }
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
