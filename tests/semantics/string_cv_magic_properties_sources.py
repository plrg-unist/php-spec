#!/usr/bin/env python3
"""Normal scalar magic GET/SET retain actual string-CV member selection."""
from pathlib import Path

import tick_sources as ticks

SOURCE = b'''<?php
$n=0;
function read77($value,$member){
    global $n;$n=$n+1;echo "H",$value,":",$member,";";
    if($n===2){unset($GLOBALS['object']);echo "U";throw new Exception("get");}
    return $value+100;
}
class MagicNameGet77 {
    private int $secret=7;
    public int $plain=99;
    public function __get($member){echo "G",$member,";";$GLOBALS['name']="plain";return read77($this->secret,$member);}
    public function __destruct(){echo "A";}
}
$object=new MagicNameGet77;$name="secret";
$result=$object->$name;echo $result;echo ":";echo $name;echo ":";echo $object->$name;echo ";";
$name="secret";$result="keep";
try{$result=$object->$name;}catch(Exception $error){echo "C";echo $result==="keep";echo ";";}
unset($error);
$object=new MagicNameGet77;$name="secret";echo $object->$name;echo ";";
unset($object);echo $n;echo "Z";
'''

SET_SOURCE = b'''<?php
$fail=false;
class MagicNameSet77 {
    private int $secret=7;
    public int $plain=99;
    public function __set(string $member,$value):void {
        echo "S",$member,":",$value,";";$GLOBALS['name']="plain";
        if($GLOBALS['fail']){throw new Exception("set");}
        $this->secret=$value*2;
    }
    public function read(){return $this->secret;}
    public function __destruct(){echo "A";}
}
$object=new MagicNameSet77;$name="secret";$input=5;
$result=($object->$name=$input);echo $result===$input;echo ":";echo $object->read();echo ":";echo $name;echo ";";
$input=9;$result=($object->$name=$input);echo $result;echo ":";echo $object->plain;echo ";";
$fail=true;$name="secret";$input=6;$result="keep";
try{$result=($object->$name=$input);}catch(Exception $error){echo "C";echo $result==="keep";echo ":";echo $object->read();echo ";";}
unset($error);
$fail=false;$name="secret";$result=($object->$name=4);echo $result===4;echo ":";echo $object->read();echo ";";
unset($object);echo "Z";
'''

SOURCE_EXPECTED = b'Gsecret;H7:secret;107:plain:99;Gsecret;H7:secret;UAC1;Gsecret;H7:secret;107;A3Z'

SET_EXPECTED = b'Ssecret:5;1:10:plain;9:9;Ssecret:6;C1:10;Ssecret:4;1:8;AZ'

CASES = {
    'cv-name-magic-get-frozen-name-and-receiver-drop': (SOURCE, SOURCE_EXPECTED),
    'cv-name-private-magic-set-input-store-abort': (SET_SOURCE, SET_EXPECTED),
}
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
