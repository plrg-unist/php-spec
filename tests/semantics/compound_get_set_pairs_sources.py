#!/usr/bin/env python3
"""Compound GET/SET uses a fixed receiver and keeps the computed result."""
from pathlib import Path

import tick_sources as ticks


PUBLIC_SOURCE = b'''<?php
$bad=false;
function plus73(){echo "R";return 2;}
function short73($input){global $bad;echo "S";return $bad?"bad":$input*10;}
class PublicCompound73 {
    public int $value=3 {
        get {echo "G";return $this->value+100;}
        set => short73($value);
    }
}
$object=new PublicCompound73;
$result=($object->value+=plus73());echo $result===105;echo ":";echo $object->value;echo ";";
$bad=true;$result="keep";
try{$result=($object->value+=plus73());}catch(TypeError $error){echo "T";echo $result==="keep";echo ":";echo $object->value;echo ";";}
unset($error);
'''

SOURCE = b'''<?php
$mode="rhs";$move=false;
function rhs73(){global $mode;echo "R";if($mode==="rhs"){throw new Exception("rhs");}return 2;}
function get73($value){
    global $mode,$move;echo "G";
    if($mode==="get"){throw new Exception("get");}
    if($move){$move=false;$GLOBALS['target']=new CompoundB73;}
    return $value+100;
}
function rewrite73($input){global $mode;echo "S";if($mode==="set"){echo "U";throw new Exception("set");}return $input*10;}
trait CompoundPair73 {
    private int $value=3 {
        get => get73($this->value);
        set(int $supplied) {
            $next=rewrite73($supplied);
            $this->value=$next;
            echo "M";echo $this->value;echo ";";
        }
    }
}
trait CompoundWrap73 {use CompoundPair73;}
class CompoundA73 {
    use CompoundWrap73;
    public static function add(){global $target;return ($target->value+=rhs73());}
    public function read(){return $this->value;}
    public function __destruct(){echo "A";}
}
class CompoundB73 {use CompoundPair73;public function read(){return $this->value;}public function __destruct(){echo "B";}}
$target=new CompoundA73;$result="keep";
try{$result=CompoundA73::add();}catch(Exception $error){echo "C";echo $result==="keep";echo ";";}
unset($error);
$mode="get";
try{$result=CompoundA73::add();}catch(Exception $error){echo "C";echo $result==="keep";echo ";";}
unset($error);
$mode="set";
try{$result=CompoundA73::add();}catch(Exception $error){echo "C";echo $result==="keep";echo ";";}
unset($error);
$mode="probe";echo $target->read();echo ";";
$mode="set";$move=true;
try{$result=CompoundA73::add();}catch(Exception $error){echo "C";echo $result==="keep";echo ";";}
unset($error);
$mode="ok";$target=new CompoundA73;
$result=CompoundA73::add();echo $result===105;echo ":";echo $target->read();echo ";";
$target=new CompoundA73;$move=true;
$result=CompoundA73::add();echo $result===105;echo ":";echo $target->read();echo ";";
try{$result=CompoundA73::add();}catch(Error $error){echo "D";echo $error->getMessage();echo "|";echo $result===105;echo ";";}
unset($error);
unset($target);echo "Z";
'''

ASYMMETRIC_SOURCE = b'''<?php
trait AsymmetricCompoundPair73 {
    public private(set) int $value=3 {
        get {echo "G";return $this->value+100;}
        set {echo "S";$this->value=$value*10;}
    }
}
class AsymmetricCompound73 {use AsymmetricCompoundPair73;}
$object=new AsymmetricCompound73;
try{$result=($object->value+=2);}catch(Error $error){echo "D";echo $error->getMessage();}
'''

SOURCE_EXPECTED = (
    b'RC1;RGC1;RGSUC1;G103;'
    b'RGSUAC1;'
    b'BRGSM1050;1:G1150;'
    b'ARGSM1050;A1:G103;'
    b'RDCannot access private property CompoundB73::$value|1;'
    b'BZ'
)

CASES = {
    'public-short-compound-computed-result-and-write-type-abort': (PUBLIC_SOURCE, b'RGS1:G1150;RGST1:G1150;'),
    'private-trait-compound-fixed-receiver-order-and-retry': (SOURCE, SOURCE_EXPECTED),
}

CONTROLS = {
    'asymmetric-trait-compound-consumer-held': (ASYMMETRIC_SOURCE, b''),
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
