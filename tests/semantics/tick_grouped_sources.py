#!/usr/bin/env python3
"""Grouped unset/global/static emitters preserve ticks between real operations."""
from pathlib import Path

import tick_sources as ticks


CASES = {
    'unset-tick-retargets-later-dynamic-name': (b'<?php $junk=0;$a=1;$b=2;$which="a";function t(){global $which;$which="b";echo "T";}register_tick_function("t");declare(ticks=1){unset($junk,${$which});}echo isset($a)?"A":"a";echo isset($b)?"B":"b";', b'TTAb'),
    'static-bindings-tick-on-cold-and-warm-calls': (b'<?php function t(){echo "T";}function f(){declare(ticks=1){static $a=0,$b=0;$a=$a+1;echo $a;}}register_tick_function("t");f();f();', b'TTT1TTTT2T'),
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
