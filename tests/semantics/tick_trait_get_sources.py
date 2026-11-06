#!/usr/bin/env python3
"""Escaped Trait GET Closures retain source, consumer scope and receiver ownership."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
$n=0;$seen=0;
function t(){
    global $n;
    $n=$n+1;echo "T";echo $GLOBALS['seen'];
    if($n===1){throw new Exception("stop");}
}
trait TickGetterTrait52 {
    public $callback {
        get => function(){
            echo self::TOKEN;
            echo get_called_class();
            declare(ticks=1){$GLOBALS['seen']=$this->other;}
            return $this->other;
        };
    }
}
class TickConsumerA52 {
    use TickGetterTrait52;
    private const TOKEN="A";
    public $other=7;
    public function __destruct(){echo "a";}
}
class TickChildA52 extends TickConsumerA52 {}
class TickConsumerB52 {
    use TickGetterTrait52;
    private const TOKEN="B";
    public $other=9;
    public function __destruct(){echo "b";}
}
register_tick_function("t");
$left=new TickChildA52;$right=new TickConsumerB52;
$a=$left->callback;$b=$right->callback;
unset($left,$right);echo "R";
try{echo $a();}catch(Exception $error){echo "C";}
unset($error);
echo $b();echo $n;
unset($a,$b);echo "Z";
'''

CASES = {
    'escaped-trait-getter-closures-retain-distinct-consumers-and-called-child':
        (SOURCE, b'RATickChildA52T7CBTickConsumerB52T992abZ'),
}
CONTROLS = {}


def main(cases=CASES, controls=CONTROLS, producer=Path(__file__)):
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(path.relative_to(ticks.ROOT)): ticks.sha(path) for path in [Path(__file__), producer]}}
    ticks.CASES, ticks.CONTROLS = cases, controls
    ticks.STATUSES = {name: 'normal' for name in cases}
    ticks.EXITS = {name: 0 for name in cases}
    ticks.main()


if __name__ == '__main__':
    main()
