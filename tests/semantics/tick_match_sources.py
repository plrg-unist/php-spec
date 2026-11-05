#!/usr/bin/env python3
"""Match tick compiler order, a parked marker and the empty-match result kind."""
from pathlib import Path

import tick_sources as ticks


HERE = Path(__file__).parent
FILES = [HERE / 'tick_match_generator.php', HERE / 'tick_match_empty.php']
CASES = {
    'match-value-across-yield': (FILES[0].read_bytes(), b'IV|TGTZ'),
    'empty-match-switch-subject': (FILES[1].read_bytes(), b'UZ'),
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
