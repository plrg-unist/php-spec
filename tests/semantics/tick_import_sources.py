#!/usr/bin/env python3
"""Ordinary/group imports each emit one Tick at their compiler name line."""
from pathlib import Path

import tick_sources as ticks


CASES = {
    'ordinary-and-group-imports-tick-once-at-name-and-prefix-lines': (rb'''<?php
function t(){$trace=(new Exception)->getTrace();echo $trace[0]["line"];echo ";";}
register_tick_function("t");
interface TickImportI47 {}
class TickImportEnable47 { public function unused(){declare(ticks=1);} }
use
    Missing47\First as AliasOne,
    Missing47\Second as AliasTwo;
class TickImportBarrier47 implements TickImportI47 {}
use
    Missing47\Group\{
        Third as AliasThree,
        Fourth as AliasFour
    };
echo "Z";
''', b'7;11;Z15;'),
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
