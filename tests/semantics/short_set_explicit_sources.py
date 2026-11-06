#!/usr/bin/env python3
"""Explicit short SET parameters keep source names, types and original inputs."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
$n=0;
function rewrite55($supplied){
    global $n;
    $n=$n+1;echo "E";echo $supplied;
    if($n===2){throw new Exception("stop");}
    if($n===4){unset($GLOBALS['object']);echo "U";throw new Exception("gone");}
    return $supplied+1;
}
class ShortSet55 {
    public int $value=0 {set(int|string $supplied) => rewrite55($supplied);}
    public function __destruct(){echo "D";echo $this->value;}
}
$object=new ShortSet55;
$result=($object->value="4");echo $result==="4";echo $object->value;
try{$object->value="9";}catch(Exception $error){echo "C";echo $object->value;}
unset($error);
$result=($object->value="2");echo $result==="2";echo $object->value;
try{$object->value="8";}catch(Exception $error){echo "C";}
unset($error);
$object=new ShortSet55;
$result=($object->value="1");echo $result==="1";echo $object->value;
unset($object);echo $n;echo "Z";
'''

CASES = {
    'explicit-short-set-supplied-name-and-contravariant-original-string':
        (b'<?php class ShortSetPlain55 {public int $value=0 {set(int|string $supplied) => $supplied+1;}} '
         b'$object=new ShortSetPlain55;echo $object->value;'
         b'$result=($object->value="5");echo $result==="5";echo $object->value;', b'016'),
    'explicit-short-set-string-input-throw-retry-and-receiver-owner':
        (SOURCE, b'E415E9C5E213E8UD3CE112D25Z'),
    'explicit-short-set-input-and-result-type-rejection':
        (b'<?php class ShortSetTyped55 {public int $value=2 {set(int|string $supplied) => [];}} '
         b'$object=new ShortSetTyped55;'
         b'try{$object->value=[];}catch(TypeError $error){echo "A";}'
         b'echo $object->value;'
         b'try{$object->value="5";}catch(TypeError $error){echo "B";}'
         b'echo $object->value;', b'A2B2'),
    'explicit-short-set-incompatible-parameter-before-main':
        (b'<?php echo "P";class ShortSetBad55 {public int $value=0 '
         b'{set(string $supplied) => missing55($supplied);}}echo "Z";', b''),
    'explicit-short-set-body-error-before-incompatible-parameter':
        (b'<?php echo "P";class ShortSetPriority55 {public int $value=0 '
         b'{set(string $supplied) => ($this=1);}}echo "Z";', b''),
}


def main():
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(Path(__file__).relative_to(ticks.ROOT)): ticks.sha(Path(__file__))}}
    ticks.CASES, ticks.CONTROLS = CASES, {}
    ticks.STATUSES = {name: 'normal' for name in CASES}
    ticks.EXITS = {name: 0 for name in CASES}
    for name in ['explicit-short-set-incompatible-parameter-before-main',
                 'explicit-short-set-body-error-before-incompatible-parameter']:
        ticks.STATUSES[name] = 'static_rejection'
        ticks.EXITS[name] = 255
    ticks.main(model_timeout=180)


if __name__ == '__main__':
    main()
