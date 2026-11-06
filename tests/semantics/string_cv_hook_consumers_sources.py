#!/usr/bin/env python3
"""String CV names retain each quiet, conditional and compound selection law."""
from pathlib import Path

import tick_sources as ticks

SOURCE = b'''<?php
$n=0;$mode=0;
function get76($backing){
    global $n,$mode;$n=$n+1;echo "G",$backing,";";$GLOBALS['name']="plain";
    if($mode===1){echo "X";throw new Exception("get");}
    if($mode===2){return 0;}
    if($mode===5){return $backing;}
    return null;
}
function rhs76(){
    global $mode;echo "R";$GLOBALS['name']="plain";
    if($mode===3){$GLOBALS['object']=$GLOBALS['other'];echo "U";throw new Exception("rhs");}
    if($mode===4){$GLOBALS['name']="value";}
    return "5";
}
function store76($entry){echo "S";$GLOBALS['name']="plain";return $entry+10;}
class ConditionalName76 {
    public ?int $value=3 {get => get76($this->value);set => store76($value);}
    public int $plain=99;
    public string $tag="A";
    public function __destruct(){echo $this->tag;}
}
$object=new ConditionalName76;$other=new ConditionalName76;$other->tag="B";$name="value";
echo isset($object->$name);echo ";";
$mode=1;$name="value";$result="keep";
try{$result=empty($object->$name);}catch(Exception $error){echo "Q";echo $result==="keep";echo ";";}
unset($error);
$mode=0;$name="value";echo ($object->$name ?? "F");echo ";";
$name="value";$result=($object->$name ??= rhs76());echo $result===5;echo ":";echo $object->plain;echo ";";
$mode=3;$name="value";$result="keep";
try{$result=($object->$name ??= rhs76());}catch(Exception $error){echo "C";echo $result==="keep";echo ";";}
unset($error);
$mode=4;$name="value";$result=($object->$name ??= rhs76());echo $result==="5";echo ":";echo $name;echo ";";
$mode=2;$name="value";echo empty($object->$name);echo ";";
$name="value";$result=($object->$name ??= rhs76());echo $result===0;echo ";";
$mode=5;$name="value";echo $object->$name;echo ";";
unset($object);unset($other);echo $n;echo "Z";
'''

COMPOUND_SOURCE = b'''<?php
$fail=false;
function compound_rhs76(){echo "R";return 2;}
function compound_get76($backing){echo "G";$GLOBALS['name']="plain";return $backing+100;}
function compound_set76($entry){
    echo "S";$GLOBALS['name']="plain";
    if($GLOBALS['fail']){throw new Exception("set");}
    return $entry*10;
}
class CompoundName76 {
    public int $value=3 {get => compound_get76($this->value);set(int $entry) => compound_set76($entry);}
    public int $plain=99;
}
$object=new CompoundName76;$name="value";
$result=($object->$name += compound_rhs76());echo $result;echo ":";echo $object->plain;echo ";";
$fail=true;$name="value";$result="keep";
try{$result=($object->$name += compound_rhs76());}catch(Exception $error){echo "C";echo $result==="keep";echo ";";}
unset($error);
$name="value";echo $object->$name;echo ";";
$object=new CompoundName76;$fail=false;$name="value";$result=($object->$name += compound_rhs76());echo $result;echo ":";echo $object->plain;echo ";";
$name="value";echo $object->$name;echo ";";
'''

SOURCE_EXPECTED = b'G3;;G3;XQ1;G3;F;G3;R1:5;G3;RAUC1;G3;RS1:plain;G15;1;G15;1;G15;15;B9Z'

COMPOUND_EXPECTED = b'RGS105:99;RGSC1;G1150;RGS105:99;G1150;'

CASES = {
    'quiet-and-conditional-cv-name-late-selection': (SOURCE, SOURCE_EXPECTED),
    'compound-cv-name-fixed-property-and-set-abort': (COMPOUND_SOURCE, COMPOUND_EXPECTED),
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
