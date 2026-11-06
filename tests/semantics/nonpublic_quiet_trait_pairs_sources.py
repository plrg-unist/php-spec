#!/usr/bin/env python3
"""Nonpublic quiet and conditional-write consumers preserve actual selectors."""
from pathlib import Path

import tick_sources as ticks


QUIET_SOURCE = b'''<?php
$abort=false;
function quiet72($value){global $abort;echo "G";if($abort){throw new Exception("quiet");}return $value;}
trait QuietPair72 {
    protected ?int $value=null {
        get => quiet72($this->value);
        set {echo "S";$this->value=$value;}
    }
}
class QuietA72 {
    use QuietPair72;
    public function has(){return isset($this->value);}
    public function blank(){return empty($this->value);}
    public function otherHas($target){return isset($target->value);}
    public function otherBlank($target){return empty($target->value);}
    public function put($entry){return ($this->value=$entry);}
}
class QuietB72 {use QuietPair72;}
class QuietGrand72 extends QuietA72 {public function own(){return isset($this->value);}}
$object=new QuietGrand72;$other=new QuietB72;
echo isset($object->value);echo ":";echo empty($object->value);echo ";";
echo $object->has();echo ":";echo $object->blank();echo ";";
$object->put(0);echo $object->own();echo ":";echo $object->blank();echo ";";
$input=$object->put("5");echo $input==="5";echo ":";echo $object->has();echo ":";echo $object->blank();echo ";";
echo $object->otherHas($other);echo ":";echo $object->otherBlank($other);echo ";";
$abort=true;$result="keep";
try{$result=$object->has();}catch(Exception $error){echo "C";echo $result==="keep";echo ";";}
unset($error);
echo isset($object->value);echo ":";echo empty($object->value);echo ";";
'''

QUIET_SOURCE_EXPECTED = (
    b':1;'
    b'G:G1;'
    b'SG1:G1;'
    b'S1:G1:G;'
    b':1;'
    b'GC1;'
    b':1;'
)

SOURCE = b'''<?php
$mode="get";
function get72($value){
    global $mode;echo "G";
    if($mode==="get"){throw new Exception("get");}
    if($mode==="rebind"){$GLOBALS['target']=new ConditionalB72;}
    return $value;
}
function rhs72(){
    global $mode;echo "R";
    if($mode==="rebind"){echo "U";throw new Exception("rhs");}
    if($mode==="deny"){$GLOBALS['target']=new ConditionalB72;echo "D";}
    return "5";
}
trait ConditionalPair72 {
    private ?int $value=null {
        get => get72($this->value);
        set {echo "S";$this->value=$value===null?null:$value+10;}
    }
}
class ConditionalA72 {
    use ConditionalPair72;
    public function fill(){global $target;return ($target->value??=rhs72());}
    public function put($entry){return ($this->value=$entry);}
    public function read(){return $this->value;}
    public function __destruct(){echo "A";}
}
class ConditionalB72 {use ConditionalPair72;public function __destruct(){echo "B";}}
$controller=new ConditionalA72;$target=new ConditionalA72;$result="keep";
try{$result=$controller->fill();}catch(Exception $error){echo "C";echo $result==="keep";echo ";";}
unset($error);
$mode="rebind";
try{$result=$controller->fill();}catch(Exception $error){echo "C";echo $result==="keep";echo ";";}
unset($error);
$mode="deny";$target=new ConditionalA72;
try{$result=$controller->fill();}catch(Error $error){echo $error->getMessage();echo "|";echo $result==="keep";echo ";";}
unset($error);
$mode="ok";$target=new ConditionalA72;
$result=$controller->fill();echo $result==="5";echo ":";echo $target->read();echo ";";
$target->put(-10);$result=$controller->fill();echo $result===0;echo ";";
unset($target);unset($controller);echo "Z";
'''

SOURCE_EXPECTED = (
    b'GC1;'
    b'GARUC1;'
    b'BGRADCannot access private property ConditionalB72::$value|'
    b'1;'
    b'BGRS1:G15;'
    b'SG1;'
    b'AAZ'
)

PUBLIC_SOURCE = b'''<?php
class PublicConditional72 {
    public ?int $value=null {
        get {echo "G";return $this->value;}
        set {echo "S";$this->value=$value===null?null:$value+10;}
    }
}
$object=new PublicConditional72;
$result=($object->value??="5");echo $result==="5";echo ":";echo $object->value;
'''

CASES = {
    'protected-quiet-null-zero-visibility-and-getter-abort': (QUIET_SOURCE, QUIET_SOURCE_EXPECTED),
    'private-conditional-borrowed-receiver-rebind-denial-and-retry': (SOURCE, SOURCE_EXPECTED),
    'public-conditional-set-result-and-persistent-store': (PUBLIC_SOURCE, b'GS1:G15'),
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
