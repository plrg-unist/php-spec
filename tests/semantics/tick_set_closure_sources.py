#!/usr/bin/env python3
"""Escaped block SET Closures retain captured values and declaring scope."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
$n=0;$seen=0;
function t(){
    global $n;
    $n=$n+1;echo "T";echo $GLOBALS['seen'];
    if($n===1){throw new Exception("stop");}
}
class TickSetClassA53 {
    private const TOKEN="A";
    public int $value=0 {
        get {return $this->value;}
        set {
            $this->value=$value;
            global $a;$a=function()use($value){
                echo self::TOKEN;echo get_called_class();
                declare(ticks=1){$GLOBALS['seen']=$value+$this->value;}
                return $this->value;
            };
            $value=99;
        }
    }
    public function __destruct(){echo "a";}
}
class TickSetChildA53 extends TickSetClassA53 {}
trait TickSetTrait53 {
    public int $value=0 {
        set {
            $this->value=$value;
            global $b;$b=function()use($value){
                echo self::TOKEN;echo get_called_class();
                declare(ticks=1){$GLOBALS['seen']=$value+$this->value;}
                return $this->value;
            };
            $value=99;
        }
    }
}
class TickSetConsumerB53 {
    use TickSetTrait53;
    private const TOKEN="B";
    public function __destruct(){echo "b";}
}
class TickSetChildB53 extends TickSetConsumerB53 {}
register_tick_function("t");
$left=new TickSetChildA53;$right=new TickSetChildB53;
$left->value=5;$right->value=9;
unset($left,$right);echo "R";
try{echo $a();}catch(Exception $error){echo "C";}
unset($error);
echo $b();echo $n;
unset($a,$b);echo "Z";
'''

CASES = {
    'escaped-block-setter-closures-retain-role-captured-values-and-consumer-scope':
        (SOURCE, b'RATickSetChildA53T10CBTickSetChildB53T1892abZ'),
}
CONTROLS = {}


def main(cases=CASES, controls=CONTROLS, producer=Path(__file__)):
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(path.relative_to(ticks.ROOT)): ticks.sha(path) for path in [Path(__file__), producer]}}
    ticks.CASES, ticks.CONTROLS = cases, controls
    ticks.STATUSES = {name: 'normal' for name in cases}
    ticks.EXITS = {name: 0 for name in cases}
    ticks.main(model_timeout=180)


if __name__ == '__main__':
    main()
