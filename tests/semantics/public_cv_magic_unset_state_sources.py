#!/usr/bin/env python3
"""Public CV unset separates ordinary clear from its stateful magic callback."""
from pathlib import Path

import tick_sources as ticks

SOURCE = b'''<?php
$count=0;
function drop83($member){
    global $count;$count=$count+1;echo "H",$member,";";
    if($count===1){unset($GLOBALS['object']);echo "U";throw new Exception("unset");}
}
class PublicCVUnset83 {
    public int $value=7;
    public int $initial;
    public int $plain=99;
    public function __unset(string $member):void {
        echo "M",$member,";";$GLOBALS['name']="plain";
        $this->value=9;
        drop83($member);
    }
    public function __destruct(){echo "A",$this->value,";";}
}
$object=new PublicCVUnset83;$name="initial";unset($object->$name);echo "I;";
$name="value";unset($object->$name);echo isset($object->value)===false,";";
$name="value";$keep="keep";
try{unset($object->$name);$keep="lost";}catch(Exception $error){echo "C",$keep,";";}
unset($error);
$object=new PublicCVUnset83;$name="value";unset($object->$name);echo isset($object->value)===false,";";
$name="value";unset($object->$name);echo $object->value,":",$object->plain,";";
unset($object);echo $count,"Z";
'''

SOURCE_EXPECTED = b'I;1;Mvalue;Hvalue;UA9;Ckeep;1;Mvalue;Hvalue;9:99;A9;2Z'

CASES = {'public-cv-unset-initial-value-clear-unset-repopulate-throw': (SOURCE, SOURCE_EXPECTED)}
CONTROLS = {}


def main():
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(Path(__file__).relative_to(ticks.ROOT)): ticks.sha(Path(__file__))}}
    ticks.CASES, ticks.CONTROLS = CASES, CONTROLS
    ticks.STATUSES = {name: 'normal' for name in CASES}
    ticks.EXITS = {name: 0 for name in CASES}
    ticks.main(model_timeout=1800)


if __name__ == '__main__':
    main()
