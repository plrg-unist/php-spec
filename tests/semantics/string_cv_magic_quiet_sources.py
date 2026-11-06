#!/usr/bin/env python3
"""Quiet magic handlers retain CV-selected NAME across the real callback handoff."""
from pathlib import Path

import tick_sources as ticks

SOURCE = b'''<?php
$n=0;$probe=false;$zero=false;
function handoff78($value,$member){
    global $n;$n=$n+1;echo "H",$member,":",$value,";";
    if($n===2){unset($GLOBALS['object']);echo "U";throw new Exception("get");}
    if($GLOBALS['zero']){return 0;}
    return $value;
}
class MagicQuietName78 {
    private int $secret=7;
    public int $plain=99;
    public function __isset(string $member):bool {echo "I",$member,";";$GLOBALS['name']="plain";return $GLOBALS['probe'];}
    public function __get($member){echo "G",$member,";";return handoff78($this->secret,$member);}
    public function __destruct(){echo "A";}
}
$object=new MagicQuietName78;$name="secret";
echo isset($object->$name);echo ";";
$name="secret";echo empty($object->$name);echo ";";
$probe=true;$name="secret";$result=empty($object->$name);echo $result===false;echo ";";
$name="secret";$result="keep";
try{$result=($object->$name ?? 9);}catch(Exception $error){echo "C";echo $result==="keep";echo ";";}
unset($error);
$object=new MagicQuietName78;$zero=true;$name="secret";$result=($object->$name ?? 9);echo $result===0;echo ";";
$probe=false;$name="secret";echo ($object->$name ?? 9);echo ";";
unset($object);echo $n;echo "Z";
'''

CONDITIONAL_SOURCE = b'''<?php
$mode=0;$fail=false;
function rhs78():int {
    echo "R";$GLOBALS['name']="plain";
    if($GLOBALS['mode']===1){throw new Exception("rhs");}
    if($GLOBALS['mode']===2){$GLOBALS['name']="secret";}
    return 5;
}
class MagicConditionalName78 {
    private int $secret=7;
    public int $plain=99;
    public function __isset(string $member):bool {echo "I",$member,";";$GLOBALS['name']="plain";return false;}
    public function __get($member){echo "G";return 0;}
    public function __set(string $member,$value):void {echo "S",$member,":",$value,";";$GLOBALS['name']="plain";if($GLOBALS['fail']){throw new Exception("set");}$this->secret=$value*2;}
    public function read(){return $this->secret;}
    public function __destruct(){echo "A";}
}
$object=new MagicConditionalName78;$name="secret";
$result=($object->$name ??= rhs78());echo $result===5;echo ":";echo $object->plain;echo ";";
$mode=1;$name="secret";$result="keep";
try{$result=($object->$name ??= rhs78());}catch(Exception $error){echo "R";echo $result==="keep";echo ";";}
unset($error);
$mode=2;$name="secret";$result=($object->$name ??= rhs78());echo $result===5;echo ":";echo $object->read();echo ";";
$fail=true;$name="secret";$result="keep";
try{$result=($object->$name ??= rhs78());}catch(Exception $error){echo "C";echo $result==="keep";echo ":";echo $object->read();echo ";";}
unset($error);
$fail=false;$name="secret";$result=($object->$name ??= rhs78());echo $result===5;echo ":";echo $object->read();echo ";";
unset($object);echo "Z";
'''

SOURCE_EXPECTED = b'Isecret;;Isecret;1;Isecret;Gsecret;Hsecret:7;1;Isecret;Gsecret;Hsecret:7;UAC1;Isecret;Gsecret;Hsecret:7;1;Isecret;9;A3Z'

CONDITIONAL_EXPECTED = b'Isecret;R1:5;Isecret;RR1;Isecret;RSsecret:5;1:10;Isecret;RSsecret:5;C1:10;Isecret;RSsecret:5;1:10;AZ'

CASES = {
    'quiet-cv-name-captured-isset-get-and-receiver-drop': (SOURCE, SOURCE_EXPECTED),
    'conditional-magic-cv-name-late-retarget-set-and-abort': (CONDITIONAL_SOURCE, CONDITIONAL_EXPECTED),
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
