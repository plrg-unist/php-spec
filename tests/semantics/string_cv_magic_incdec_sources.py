#!/usr/bin/env python3
"""Magic CV updates retain OLD/NEW and selected property across callbacks."""
from pathlib import Path

import tick_sources as ticks

SOURCE = b'''<?php
$count=0;
function transform81($value,$member){
    global $count;$count=$count+1;echo "T",$member,":",$value,";";
    if($count===2){echo "U";throw new Exception("set");}
    return $value*2;
}
class MagicUpdateName81 {
    private int $secret=7;
    public int $plain=99;
    public string $tag="A";
    public function __get($member){
        echo "G",$member,":",$this->tag,";";
        $GLOBALS['name']="plain";$GLOBALS['object']=$GLOBALS['a'];
        return $this->secret;
    }
    public function __set(string $member,$value):void {
        echo "S",$member,":",$value,":",$this->tag,";";
        $stored=transform81($value,$member);
        $this->secret=$stored;
    }
    public function read():int {return $this->secret;}
    public function __destruct(){echo "D",$this->tag,":",$this->secret,";";}
}
$a=new MagicUpdateName81;
$object=new MagicUpdateName81;$object->tag="B";$name="secret";
$result=++$object->$name;echo $result,":",$object->read(),":",$object->plain,";";
$object=new MagicUpdateName81;$object->tag="B";$name="secret";$result="keep";
try{$result=$object->$name--;}catch(Exception $error){echo "C",$result,";";}
unset($error);
$object=new MagicUpdateName81;$object->tag="B";$name="secret";
$result=$object->$name--;echo $result,":",$object->read(),":",$object->plain,";";
unset($object,$a);echo $count,"Z";
'''

SOURCE_EXPECTED = b'Gsecret:B;Ssecret:8:B;Tsecret:8;DB:16;8:7:99;Gsecret:B;Ssecret:6:B;Tsecret:6;UDB:7;Ckeep;Gsecret:B;Ssecret:6:B;Tsecret:6;DB:12;7:7:99;DA:7;3Z'

CASES = {'cv-name-magic-preinc-postdec-fixed-selection-result-store-abort': (SOURCE, SOURCE_EXPECTED)}
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
