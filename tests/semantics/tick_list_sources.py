#!/usr/bin/env python3
"""By-value destructuring compiles RHS, nested keys and writable targets in order."""
from pathlib import Path

import tick_sources as ticks


CASES = {
    'nested-list-ticks-follow-rhs-key-key-target-order': (b'''<?php
$out=[];
function t(){echo "T";}
register_tick_function("t");
declare(ticks=1){
    list(
        (function(){declare(ticks=2);echo "K";return "a";})() =>
        list(
            (function(){declare(ticks=3);echo "J";return "b";})() =>
            $out[(function(){declare(ticks=1);echo "V";return 0;})()]
        )
    )=(function(){declare(ticks=4);echo "R";return ["a"=>["b"=>9]];})();
    echo "Z";
}
echo $out[0];
''', b'RTKJTTVTTZT9'),
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
