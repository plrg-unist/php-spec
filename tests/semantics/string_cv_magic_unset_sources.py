#!/usr/bin/env python3
"""Private magic unset retains its CV-selected name across handler effects."""
from pathlib import Path

import tick_sources as ticks

SOURCE = b'''<?php
$n=0;
function release79($member,$value){
    global $n;$n=$n+1;echo "H",$member,":",$value,";";
    if($n===2){unset($GLOBALS['object']);echo "U";throw new Exception("unset");}
}
class MagicUnsetName79 {
    private int $secret=7;
    public int $plain=99;
    public function __unset(string $member):void {
        echo "X",$member,";";$GLOBALS['name']="plain";
        release79($member,$this->secret);
        $this->secret=$this->secret+1;
    }
    public function read():int {return $this->secret;}
    public function __destruct(){echo "A";}
}
$object=new MagicUnsetName79;$name="secret";
unset($object->$name);echo $object->read(),":",$object->plain,":",$name,";";
$name="secret";$keep="keep";
try{unset($object->$name);$keep="lost";}catch(Exception $error){echo "C",$keep,";";}
unset($error);
$object=new MagicUnsetName79;$name="secret";
unset($object->$name);echo $object->read(),":",$object->plain,";";
unset($object);echo $n,"Z";
'''

SOURCE_EXPECTED = b'Xsecret;Hsecret:7;8:99:plain;Xsecret;Hsecret:8;UACkeep;Xsecret;Hsecret:7;8:99;A3Z'

CASES = {'cv-name-private-magic-unset-store-drop-throw-retry': (SOURCE, SOURCE_EXPECTED)}
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
