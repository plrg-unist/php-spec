#!/usr/bin/env python3
"""Grouped Echo ticks execute before evaluating each later operand."""
from pathlib import Path

import tick_sources as ticks


CASES = {
    'between-operand-tick-updates-later-cv': (b'<?php $x=1;function t(){global $x;$x=2;echo "T";}register_tick_function("t");declare(ticks=1){echo "A",$x;}unregister_tick_function("t");', b'AT2T'),
    'between-operand-tick-crosses-output-chunk-return': (b'<?php $x=1;$n=0;function t(){global $x;$x=2;echo "T";}function h($s){global $n;$n=$n+1;return $s;}register_tick_function("t");ob_start("h",1);declare(ticks=1){echo "A",$x;}unregister_tick_function("t");ob_end_flush();echo $n;', b'AT2T5'),
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
