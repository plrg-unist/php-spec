#!/usr/bin/env python3
"""Short SET expressions write their result and retain the caller's input."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
$n=0;
function rewrite54($value){
    global $n;
    $n=$n+1;echo "E";echo $value;
    if($n===2){throw new Exception("stop");}
    if($n===4){unset($GLOBALS['object']);echo "U";throw new Exception("gone");}
    return $value+1;
}
class ShortSet54 {
    public int $value=0 {set => rewrite54($value);}
    public function __destruct(){echo "D";echo $this->value;}
}
$object=new ShortSet54;
$result=($object->value=4);echo $result;echo $object->value;
try{$object->value=9;}catch(Exception $error){echo "C";echo $object->value;}
unset($error);
$result=($object->value=2);echo $result;echo $object->value;
try{$object->value=8;}catch(Exception $error){echo "C";}
unset($error);
$object=new ShortSet54;
$result=($object->value=1);echo $result;echo $object->value;
unset($object);echo $n;echo "Z";
'''

CASES = {
    'short-set-expression-keeps-input-result-and-transformed-backing':
        (b'<?php class ShortSetPlain54 {public int $value=0 {set => $value+1;}} '
         b'$object=new ShortSetPlain54;echo $object->value;'
         b'$result=($object->value=5);echo $result;echo $object->value;', b'056'),
    'short-set-expression-throw-retry-and-last-receiver-owner':
        (SOURCE, b'E445E9C5E223E8UD3CE112D25Z'),
    'short-set-expression-checks-input-before-body-and-result-before-write':
        (b'<?php class ShortSetTyped54 {public int $value=2 {set => [];}} '
         b'$object=new ShortSetTyped54;'
         b'try{$object->value=[];}catch(TypeError $error){echo "A";}'
         b'echo $object->value;'
         b'try{$object->value=5;}catch(TypeError $error){echo "B";}'
         b'echo $object->value;', b'A2B2'),
}
CONTROLS = {}


def main():
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(Path(__file__).relative_to(ticks.ROOT)): ticks.sha(Path(__file__))}}
    ticks.CASES, ticks.CONTROLS = CASES, CONTROLS
    ticks.STATUSES = {name: 'normal' for name in CASES}
    ticks.EXITS = {name: 0 for name in CASES}
    ticks.main(model_timeout=180)


if __name__ == '__main__':
    main()
