#!/usr/bin/env python3
"""Magic integer += fixes its CV-selected property across GET and SET."""
from pathlib import Path

import tick_sources as ticks

SOURCE = b'''<?php
$count=0;
function rhs80():int {echo "R";$GLOBALS['object']=$GLOBALS['next'];$GLOBALS['name']="secret";return 2;}
function transform80($value,$member){
    global $count;$count=$count+1;echo "T",$member,":",$value,";";
    if($count===2){echo "U";throw new Exception("set");}
    return $value*2;
}
class MagicAddName80 {
    private int $secret=7;
    public int $plain=99;
    public string $tag="A";
    public function __get($member){
        echo "G",$member,":",$this->tag,";";
        $GLOBALS['name']="plain";$GLOBALS['object']=$GLOBALS['a'];unset($GLOBALS['next']);
        return $this->secret;
    }
    public function __set(string $member,$value):void {
        echo "S",$member,":",$value,":",$this->tag,";";
        $stored=transform80($value,$member);
        $this->secret=$stored;
    }
    public function read():int {return $this->secret;}
    public function __destruct(){echo "D",$this->tag,":",$this->secret,";";}
}
$a=new MagicAddName80;$object=$a;
$next=new MagicAddName80;$next->tag="B";$name="plain";
$result=($object->$name += rhs80());echo $result,":",$object->read(),":",$object->plain,";";
$next=new MagicAddName80;$next->tag="B";$name="plain";$result="keep";
try{$result=($object->$name += rhs80());}catch(Exception $error){echo "C",$result,";";}
unset($error);
$next=new MagicAddName80;$next->tag="B";$name="plain";
$result=($object->$name += rhs80());echo $result,":",$object->read(),":",$object->plain,";";
unset($object,$a);echo $count,"Z";
'''

SOURCE_EXPECTED = b'RGsecret:B;Ssecret:9:B;Tsecret:9;DB:18;9:7:99;RGsecret:B;Ssecret:9:B;Tsecret:9;UDB:7;Ckeep;RGsecret:B;Ssecret:9:B;Tsecret:9;DB:18;9:7:99;DA:7;3Z'

CASES = {'cv-name-magic-add-fixed-selection-input-store-throw-retry': (SOURCE, SOURCE_EXPECTED)}
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
