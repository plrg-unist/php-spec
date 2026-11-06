#!/usr/bin/env python3
"""Normal backed-pair hooks retain a selected string-CV property name."""
from pathlib import Path

import tick_sources as ticks

SOURCE = b'''<?php
$n=0;
function read75($backing){
    global $n;$n=$n+1;echo "G",$backing,";";
    if($n===2){$GLOBALS['name']="plain";unset($GLOBALS['object']);echo "U";throw new Exception("gone");}
    return $backing+100;
}
function store75($entry){echo "S";$GLOBALS['name']="plain";return $entry*2;}
trait PrivateNamePair75 {
    private int $value=3 {
        set(int $entry) => store75($entry);
        get => read75($this->value);
    }
}
trait PrivateNameWrapper75 {use PrivateNamePair75;}
class PrivateNameA75 {
    use PrivateNameWrapper75;
    public int $plain=99;
    public function put($entry){global $name;return ($this->$name=$entry);}
    public function read(){global $name;return $this->$name;}
    public function other($target){global $name;return $target->$name;}
    public function __destruct(){echo "A";}
}
class PrivateNameB75 {use PrivateNamePair75;public function read(){global $name;return $this->$name;}public function __destruct(){echo "B";}}
$object=new PrivateNameA75;$other=new PrivateNameB75;$name="value";
$input="5";$result=$object->put($input);echo $result===$input;echo ":";echo $name;echo ";";
$name="value";$result=$object->read();echo $result;echo ";";
try{$object->other($other);}catch(Error $error){echo "D";echo $error->getMessage();echo ";";}
unset($error);
try{$object->put([]);}catch(TypeError $error){echo "T";}
unset($error);
try{$result=$object->read();}catch(Exception $error){echo "C";echo $result===110;echo ":";echo $name;echo ";";}
unset($error);
$object=new PrivateNameA75;$name="value";$result=$object->put("2");echo $result==="2";echo ";";
$name="value";echo $object->read();echo ";";echo $other->read();echo ";";
unset($object);unset($other);echo $n;echo "Z";
'''

PUBLIC_SOURCE = b'''<?php
function rhs75(){echo "R";$GLOBALS['name']="plain";return "5";}
function public_store75($entry){echo "S";$GLOBALS['name']="plain";return $entry*2;}
function public_read75($backing){echo "G";$GLOBALS['name']="plain";return $backing+100;}
class PublicName75 {
    public int $value=3 {get => public_read75($this->value);set(int $entry) => public_store75($entry);}
    public int $plain=99;
}
$object=new PublicName75;$name="value";
$result=($object->$name=rhs75());echo $result==="5";echo ":";echo $object->plain;echo ";";
$name="value";$input="4";$result=($object->$name=$input);echo $result===$input;echo ":";echo $name;echo ":";echo $object->plain;echo ";";
$name="value";echo $object->$name;echo ":";echo $name;echo ";";
$name="value";$result="keep";try{$result=($object->$name=[]);}catch(TypeError $error){echo "T";echo $result==="keep";echo ";";}
unset($error);
$name="value";echo $object->$name;echo ";";
'''

STRINGABLE_SOURCE = b'''<?php
class NameObject75 {public function __toString(){echo "N";return "value";}}
class NameStringableTarget75 {public int $value=3 {get => $this->value;set => $value;}}
$object=new NameStringableTarget75;$name=new NameObject75;echo $object->$name;
'''


SOURCE_EXPECTED = b'S1:plain;G10;110;DCannot access private property PrivateNameB75::$value;TG10;UAC1:plain;S1;G4;104;G3;103;AB4Z'

PUBLIC_EXPECTED = b'R:5;S1:plain:5;G108:plain;T1;G108;'

CASES = {
    'private-dynamic-name-selected-key-owner-abort': (SOURCE, SOURCE_EXPECTED),
    'public-dynamic-name-rhs-and-hook-rebinding': (PUBLIC_SOURCE, PUBLIC_EXPECTED),
}

CONTROLS = {
    'stringable-name-outside-plain-cv-slice': (STRINGABLE_SOURCE, b''),
}


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
