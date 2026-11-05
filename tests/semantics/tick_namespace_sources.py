#!/usr/bin/env python3
"""Namespace source form determines whether its Tick precedes or follows its body."""
from pathlib import Path

import tick_sources as ticks


CASES = {
    'semicolon-namespace-header-does-not-retick-after-its-body': (b'''<?php
namespace TickNs46;
function t(){echo "T";}
register_tick_function('TickNs46\\t');
class C { public function unused(){declare(ticks=1);} }
''', b''),
    'braced-namespace-emits-after-body-declarables': (b'''<?php
namespace TickNs46 {
function t(){echo "T";}
register_tick_function('TickNs46\\t');
class C { public function unused(){declare(ticks=1);} }
}
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
