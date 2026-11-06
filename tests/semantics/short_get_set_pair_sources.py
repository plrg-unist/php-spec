#!/usr/bin/env python3
"""Block GET and short SET share a backing slot with separate hook identities."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
$n=0;
function rewrite56($supplied,$backing){
    global $n;
    $n=$n+1;echo "S";echo $supplied;echo ":";echo $backing;echo ";";
    if($n===2){throw new Exception("stop");}
    if($n===4){unset($GLOBALS['object']);echo "U";throw new Exception("gone");}
    return $supplied+$backing+10;
}
class ShortGetSetPair56 {
    public int $value=0 {
        get {
            echo "G";
            $this->value=$this->value+1;
            return $this->value+100;
        }
        set(int|string $supplied) => rewrite56($supplied,$this->value);
    }
    public function __destruct(){echo "D";}
}
$object=new ShortGetSetPair56;
$result=($object->value="4");echo $result==="4";echo $object->value;
try{$object->value="9";}catch(Exception $error){echo "C";echo $object->value;}
unset($error);
$result=($object->value="2");echo $result==="2";echo $object->value;
try{$object->value="8";}catch(Exception $error){echo "C";}
unset($error);
$object=new ShortGetSetPair56;
$result=($object->value="1");echo $result==="1";echo $object->value;
unset($object);echo $n;echo "Z";
'''

CASES = {
    'class-block-get-short-implicit-set-crossed-backing-access':
        (b'<?php class ShortPairPlain56 {public int $value=0 '
         b'{get {echo "G";$this->value=$this->value+1;return $this->value+100;}'
         b'set => $value+$this->value+10;}} '
         b'$object=new ShortPairPlain56;$result=($object->value=5);'
         b'echo $result;echo $object->value;', b'5G116'),
    'class-block-get-short-explicit-set-results-throw-retry-and-receiver':
        (SOURCE, b'S4:0;1G115S9:15;CG116S2:16;1G129S8:29;UDCS1:0;1G112D5Z'),
    'class-block-get-error-before-short-set-variance-error':
        (b'<?php echo "P";class ShortPairPriority56 {public int $value=0 '
         b'{get {$this=1;return $this->value;}set(string $supplied) => $supplied;}}'
         b'echo "Z";', b''),
}
CONTROLS = {
    'trait-short-set-pair-remains-unsupported':
        (b'<?php trait ShortPairTrait56 {public int $value=0 '
         b'{get {return $this->value;}set => $value+1;}} '
         b'class ShortPairConsumer56 {use ShortPairTrait56;}echo "X";', b''),
}


def main():
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(Path(__file__).relative_to(ticks.ROOT)): ticks.sha(Path(__file__))}}
    ticks.CASES, ticks.CONTROLS = CASES, CONTROLS
    ticks.STATUSES = {name: 'normal' for name in CASES}
    ticks.EXITS = {name: 0 for name in CASES}
    name = 'class-block-get-error-before-short-set-variance-error'
    ticks.STATUSES[name], ticks.EXITS[name] = 'static_rejection', 255
    ticks.main(model_timeout=180)


if __name__ == '__main__':
    main()
