#!/usr/bin/env python3
"""Pure GET and short SET preserve genuinely uninitialized backing before first write."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
$n=0;
function rewrite58($supplied){
    global $n;
    $n=$n+1;echo "S";echo $supplied;echo ";";
    if($n===1){unset($GLOBALS['object']);echo "U";throw new Exception("gone");}
    if($n===3){throw new Exception("stop");}
    return $supplied+10;
}
class ShortGetSetPair58 {
    public int $value {
        get {
            echo "G";
            return 700;
        }
        set(int|string $supplied) => rewrite58($supplied);
    }
    public function __destruct(){echo "D";}
}
$object=new ShortGetSetPair58;echo $object->value;
$result="keep";
try{$result=($object->value="4");}catch(Exception $error){echo "C";echo $result==="keep";}
unset($error);
$object=new ShortGetSetPair58;echo $object->value;
$result=($object->value="5");echo $result==="5";echo $object->value;
try{$result=($object->value="9");}catch(Exception $error){echo "C";echo $result==="5";echo $object->value;}
unset($error);
$result=($object->value="2");echo $result==="2";echo $object->value;
unset($object);echo $n;echo "Z";
'''

TYPES_SOURCE = b'''<?php
function peek58($backing){echo "K";echo $backing;return $backing;}
function bad58(){echo "R";return "bad";}
class PureShortPairTypes58 {
    public int $value {
        get {echo "G";return 700;}
        set(int|string $supplied) => $supplied==="bad" ? bad58() : ($supplied===0 ? peek58($this->value) : $supplied+10);
    }
}
$object=new PureShortPairTypes58;echo $object->value;
try{$object->value=[];}catch(TypeError $error){echo "A";}
try{$object->value=0;}catch(Error $error){echo $error->getMessage();echo "|";}
echo $object->value;
try{$object->value="bad";}catch(TypeError $error){echo "B";}
try{$object->value=0;}catch(Error $error){echo $error->getMessage();echo "|";}
$result=($object->value="5");echo $result==="5";echo $object->value;
$result=($object->value=0);echo $result;
try{$object->value="bad";}catch(TypeError $error){echo "T";}
$result=($object->value=0);echo $result;
$result=($object->value="2");echo $result==="2";echo $object->value;
$result=($object->value=0);echo $result;
'''
UNINITIALIZED = b'Typed property PureShortPairTypes58::$value must not be accessed before initialization|'

CASES = {
    'class-uninitialized-pure-get-implicit-short-set-first-write':
        (b'<?php class UninitializedShortPairPlain58 {public int $value '
         b'{get {echo "G";return 700;}set => $value+10;}} '
         b'$object=new UninitializedShortPairPlain58;echo $object->value;'
         b'$result=($object->value=5);echo $result;echo $object->value;'
         b'$result=($object->value=9);echo $result;echo $object->value;',
         b'G7005G7009G700'),
    'class-uninitialized-pure-get-short-set-type-aborts-backing-read-and-retry':
        (TYPES_SOURCE, b'G700A'+UNINITIALIZED+b'G700RB'+UNINITIALIZED+
         b'1G700K150RTK1501G700K120'),
    'class-uninitialized-pure-get-first-write-abort-retry-and-receiver':
        (SOURCE, b'G700S4;UDC1G700S5;1G700S9;C1G700S2;1G700D4Z'),
    'uninitialized-pure-get-error-before-short-set-variance-error':
        (b'<?php echo "P";class UninitializedShortPairPriority58 {public int $value '
         b'{get {$this=1;return 700;}set(string $supplied) => $supplied;}}'
         b'echo "Z";', b''),
}
CONTROLS = {
    'trait-uninitialized-pure-get-short-set-pair-remains-unsupported':
        (b'<?php trait UninitializedShortPairTrait58 {public int $value '
         b'{get {return 700;}set => $value+1;}} '
         b'class UninitializedShortPairConsumer58 {use UninitializedShortPairTrait58;}echo "X";', b''),
}


def main():
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(Path(__file__).relative_to(ticks.ROOT)): ticks.sha(Path(__file__))}}
    ticks.CASES, ticks.CONTROLS = CASES, CONTROLS
    ticks.STATUSES = {name: 'normal' for name in CASES}
    ticks.EXITS = {name: 0 for name in CASES}
    name = 'uninitialized-pure-get-error-before-short-set-variance-error'
    ticks.STATUSES[name], ticks.EXITS[name] = 'static_rejection', 255
    ticks.main(model_timeout=180)


if __name__ == '__main__':
    main()
