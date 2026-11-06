#!/usr/bin/env python3
"""A pure initialized block GET shares the short SET intrinsic backing slot."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
$n=0;
function rewrite57($supplied){
    global $n;
    $n=$n+1;echo "S";echo $supplied;echo ";";
    if($n===2){throw new Exception("stop");}
    if($n===4){unset($GLOBALS['object']);echo "U";throw new Exception("gone");}
    return $supplied+10;
}
class ShortGetSetPair57 {
    public int $value=0 {
        get {
            echo "G";
            return 700;
        }
        set(int|string $supplied) => rewrite57($supplied);
    }
    public function __destruct(){echo "D";}
}
$object=new ShortGetSetPair57;
$result=($object->value="4");echo $result==="4";echo $object->value;
try{$object->value="9";}catch(Exception $error){echo "C";echo $object->value;}
unset($error);
$result=($object->value="2");echo $result==="2";echo $object->value;
try{$object->value="8";}catch(Exception $error){echo "C";}
unset($error);
$object=new ShortGetSetPair57;
$result=($object->value="1");echo $result==="1";echo $object->value;
unset($object);echo $n;echo "Z";
'''

CASES = {
    'class-pure-get-intrinsically-backed-implicit-short-set':
        (b'<?php class PureShortPairPlain57 {public int $value=3 '
         b'{get {echo "G";return 700;}set => $value+10;}} '
         b'$object=new PureShortPairPlain57;$result=($object->value=5);'
         b'echo $result;echo $object->value;$result=($object->value=9);'
         b'echo $result;echo $object->value;', b'5G7009G700'),
    'class-pure-get-explicit-short-set-results-throw-retry-and-receiver':
        (SOURCE, b'S4;1G700S9;CG700S2;1G700S8;UDCS1;1G700D5Z'),
    'class-pure-get-short-set-observes-persistent-backing':
        (b'<?php function trackBacking57($supplied,$backing){'
         b'echo "S";echo $supplied;echo ":";echo $backing;echo ";";'
         b'return $supplied+$backing+10;}'
         b'class PureShortPairBacking57 {public int $value=3 '
         b'{get {echo "G";return 700;}set => trackBacking57($value,$this->value);}} '
         b'$object=new PureShortPairBacking57;$result=($object->value=5);'
         b'echo $result;echo $object->value;$result=($object->value=2);'
         b'echo $result;echo $object->value;', b'S5:3;5G700S2:18;2G700'),
    'pure-get-error-before-short-set-variance-error':
        (b'<?php echo "P";class PureShortPairPriority57 {public int $value=0 '
         b'{get {$this=1;return 700;}set(string $supplied) => $supplied;}}'
         b'echo "Z";', b''),
}
CONTROLS = {
}

def main():
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(Path(__file__).relative_to(ticks.ROOT)): ticks.sha(Path(__file__))}}
    ticks.CASES, ticks.CONTROLS = CASES, CONTROLS
    ticks.STATUSES = {name: 'normal' for name in CASES}
    ticks.EXITS = {name: 0 for name in CASES}
    name = 'pure-get-error-before-short-set-variance-error'
    ticks.STATUSES[name], ticks.EXITS[name] = 'static_rejection', 255
    ticks.main(model_timeout=180)


if __name__ == '__main__':
    main()
