#!/usr/bin/env python3
"""Class-like compiler facts preserve declaration adjacency and member ticks."""
from pathlib import Path

import tick_sources as ticks


CASES = {
    'early-class-keeps-prior-marker-and-compiles-method-declarables': (b'''<?php
function t(){echo "T";}
register_tick_function("t");
declare(ticks=1);
class TickEarly39 {
    public static function unused(){declare(ticks=2);echo "BAD";}
    public static function run(){declare(ticks=1){echo "M";}}
}
1;
echo "Z";
TickEarly39::run();
echo "W";
''', b'TZMTWT'),
    'conditional-class-tick-sees-activation-before-callback-abort': (b'''<?php
$n=0;
function t(){
    global $n;
    $n=$n+1;
    echo "T";
    if($n===2){
        $at=new Exception;
        echo "[".$at->getTrace()[0]["line"]."]";
        echo (new TickLate39)->get();
        throw new Exception("stop");
    }
}
register_tick_function("t");
declare(ticks=1);
try{
    if(true){
        class TickLate39{
            public function get(){return 7;}
        }
    }
    echo "BAD";
}catch(Exception $e){echo "C";}
echo "Z";
''', b'TT[18]7CTZT'),
}

def main(cases=CASES, producer=Path(__file__), controls=None):
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(path.relative_to(ticks.ROOT)): ticks.sha(path) for path in [Path(__file__), producer]}}
    ticks.CASES = cases
    ticks.CONTROLS = controls or {}
    ticks.STATUSES = {name: 'normal' for name in cases}
    ticks.EXITS = {name: 0 for name in cases}
    ticks.main()


if __name__ == '__main__':
    main()
