#!/usr/bin/env python3
"""Direct hooked UNSET keeps canonical keys and forbids backing deletion."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
function release74(){unset($GLOBALS['object']);echo "U";}
trait PrivateUnsetPair74 {
    private int $value=7 {
        get {echo "G";return $this->value+100;}
        set {echo "S";$this->value=$value*2;}
    }
}
trait PrivateUnsetWrap74 {use PrivateUnsetPair74;}
class PrivateUnsetA74 {
    use PrivateUnsetWrap74;
    public function put($input){return ($this->value=$input);}
    public function read(){return $this->value;}
    public function other($target){unset($target->value);}
    public function erase($drop){if($drop){release74();}unset($this->value);}
    public function __destruct(){echo "A";}
}
class PrivateUnsetB74 {use PrivateUnsetPair74;public function read(){return $this->value;}public function __destruct(){echo "B";}}
$object=new PrivateUnsetA74;$other=new PrivateUnsetB74;
try{unset($object->value);}catch(Error $error){echo "V";echo $error->getMessage();echo ";";}
unset($error);
$input="5";$result=$object->put($input);echo $result===$input;echo ";";
$result="keep";
try{$result=$object->erase(false);}catch(Error $error){echo "E";echo $error->getMessage();echo "|";echo $result==="keep";echo ";";}
unset($error);
echo $object->read();echo ";";
try{$result=$object->other($other);}catch(Error $error){echo "X";echo $error->getMessage();echo "|";echo $result==="keep";echo ";";}
unset($error);
echo $other->read();echo ";";
try{$result=$object->erase(true);}catch(Error $error){echo "L";echo $error->getMessage();echo "|";echo $result==="keep";echo ";";}
unset($error);
unset($other);echo "Z";
'''

PROTECTED_SOURCE = b'''<?php
trait ProtectedUnsetPair74 {
    protected int $value=7 {
        get {
            echo "G";
            try{unset($this->value);}catch(Error $error){echo "I";echo $error->getMessage();echo ";";}
            return $this->value+100;
        }
        set(int $input) {
            echo "S";
            try{unset($this->value);}catch(Error $error){echo "J";echo $error->getMessage();echo ";";}
            $this->value=$input*2;
        }
    }
}
class ProtectedUnsetA74 {use ProtectedUnsetPair74;public function read(){return $this->value;}public function put($input){return ($this->value=$input);}}
class ProtectedUnsetGrand74 extends ProtectedUnsetA74 {public function erase(){unset($this->value);}}
$object=new ProtectedUnsetGrand74;
try{unset($object->value);}catch(Error $error){echo "V";echo $error->getMessage();echo ";";}
unset($error);
echo $object->read();echo ";";
$input="5";$result=$object->put($input);echo $result===$input;echo ";";
try{unset($object->value);}catch(Error $error){echo "W";echo $error->getMessage();echo ";";}
unset($error);
try{$object->erase();}catch(Error $error){echo "E";echo $error->getMessage();echo ";";}
unset($error);
echo $object->read();echo ";";
'''

INDIRECT_SOURCE = b'''<?php
trait IndirectUnsetPair74 {
    private int $value=7 {
        get {echo "G";return $this->value;}
        set {$this->value=$value;}
    }
}
class IndirectUnset74 {use IndirectUnsetPair74;public function erase(){unset($this->value[0]);}}
$object=new IndirectUnset74;
try{$object->erase();}catch(Error $error){echo "D";echo $error->getMessage();}
'''

SOURCE_EXPECTED = (
    b'VCannot access private property PrivateUnsetA74::$value;S1;'
    b'ECannot unset hooked property PrivateUnsetA74::$value|1;G110;'
    b'XCannot access private property PrivateUnsetB74::$value|1;G107;'
    b'UALCannot unset hooked property PrivateUnsetA74::$value|1;BZ'
)

PROTECTED_EXPECTED = (
    b'VCannot access protected property ProtectedUnsetGrand74::$value;'
    b'GICannot unset hooked property ProtectedUnsetGrand74::$value;107;'
    b'SJCannot unset hooked property ProtectedUnsetGrand74::$value;1;'
    b'WCannot access protected property ProtectedUnsetGrand74::$value;'
    b'ECannot unset hooked property ProtectedUnsetGrand74::$value;'
    b'GICannot unset hooked property ProtectedUnsetGrand74::$value;110;'
)

CASES = {
    'private-unset-canonical-key-visibility-and-last-owner': (SOURCE, SOURCE_EXPECTED),
    'protected-unset-own-hooks-and-descendant-scope': (PROTECTED_SOURCE, PROTECTED_EXPECTED),
}

CONTROLS = {
    'private-hook-indirect-unset-held': (INDIRECT_SOURCE, b''),
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
