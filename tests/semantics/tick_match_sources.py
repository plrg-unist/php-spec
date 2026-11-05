#!/usr/bin/env python3
"""Match tick compiler order, a parked marker and the empty-match result kind."""
from pathlib import Path

import tick_sources as ticks


HERE = Path(__file__).parent
FILES = [HERE / 'tick_match_generator.php', HERE / 'tick_match_empty.php']
CASES = {
    'match-value-across-yield': (FILES[0].read_bytes(), b'IV|TGTZ'),
    'empty-match-switch-subject': (FILES[1].read_bytes(), b'UZ'),
    'nonempty-match-switch-temporary': (b'<?php function t(){echo "T";}register_tick_function("t");declare(ticks=1){echo "P";switch(match(0){0=>1}){case 1:echo "A";break;default:echo "B";}echo "Z";}unregister_tick_function("t");', b'PTATTZT'),
}


def main(cases=CASES, producer=Path(__file__)):
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(path.relative_to(ticks.ROOT)): ticks.sha(path) for path in [Path(__file__), producer, *FILES]}}
    ticks.CASES, ticks.CONTROLS = cases, {}
    ticks.STATUSES = {name: 'normal' for name in cases}
    ticks.EXITS = {name: 0 for name in cases}
    ticks.main()


if __name__ == '__main__':
    main()
