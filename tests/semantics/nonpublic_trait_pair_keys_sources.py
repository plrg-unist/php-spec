#!/usr/bin/env python3
"""Nonpublic backed Trait pairs preserve raw names and actual Consumer keys."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
$n=0;
function read71($backing,$lexical,$called){
    global $n;$n=$n+1;
    echo "G",$backing,":",$lexical,":",$called,";";
    if($n===2){unset($GLOBALS['object']);echo "U";throw new Exception("gone");}
    return $backing+100;
}
trait PrivatePair71 {
    private int $value=3 {
        set(int $entry) => $entry+10;
        get => read71($this->value,__CLASS__,static::class);
    }
}
trait PrivateWrapper71 {use PrivatePair71;}
class ConsumerA71 {
    use PrivateWrapper71;
    public function put($entry){return ($this->value=$entry);}
    public function read(){return $this->value;}
    public function other($target){return $target->value;}
    public function __destruct(){echo "A";}
}
class ConsumerB71 {
    use PrivatePair71;
    public function put($entry){return ($this->value=$entry);}
    public function read(){return $this->value;}
    public function __destruct(){echo "B";}
}
class GrandA71 extends ConsumerA71 {public function own(){return $this->value;}}
$object=new GrandA71;$other=new ConsumerB71;
$input=$object->put("5");echo $input==="5";echo ";";
$result=$object->read();echo $result;echo ";";
try{$object->other($other);}catch(Error $error){echo $error->getMessage();echo "|";}
unset($error);
$other->put("7");
try{$missing=$object->own();echo "N";echo $missing===null;echo ";";}catch(Error $error){echo "E";echo $error->getMessage();echo "|";}
unset($error);
try{$object->put([]);}catch(TypeError $error){echo "T";}
unset($error);
try{$result=$object->read();}catch(Exception $error){echo "C";echo $result===115;echo ";";}
unset($error);
echo $other->read();echo ";";
$object=new GrandA71;$input=$object->put("2");echo $input==="2";echo ";";echo $object->read();echo ";";
unset($object);unset($other);echo $n;echo "Z";
'''

SOURCE_EXPECTED = (
    b'1;'
    b'G15:ConsumerA71:GrandA71;'
    b'115;'
    b'Cannot access private property ConsumerB71::$value|'
    b'N1;'
    b'TG15:ConsumerA71:GrandA71;'
    b'UAC1;'
    b'G17:ConsumerB71:ConsumerB71;'
    b'117;'
    b'1;'
    b'G12:ConsumerA71:GrandA71;'
    b'112;'
    b'AB4Z'
)

PROTECTED_SOURCE = b'''<?php
trait ProtectedPair71 {
    protected int $value {
        get {return $this->value+100;}
        set(int|string $entry){$this->value=$entry+20;}
    }
}
class ProtectedA71 {
    use ProtectedPair71;
    public function put($entry){return ($this->value=$entry);}
    public function read(){return $this->value;}
    public function other($target){return $target->value;}
}
class ProtectedB71 {use ProtectedPair71;public function put($entry){return ($this->value=$entry);}public function read(){return $this->value;}}
class ProtectedGrand71 extends ProtectedA71 {public function own(){return $this->value;}}
$object=new ProtectedGrand71;$other=new ProtectedB71;
try{echo $object->value;}catch(Error $error){echo $error->getMessage();echo "|";}
unset($error);
try{echo $object->own();}catch(Error $error){echo $error->getMessage();echo "|";}
unset($error);
try{$object->other($other);}catch(Error $error){echo $error->getMessage();echo "|";}
unset($error);
$result=$object->put("4");echo $result==="4";echo ":";echo $object->own();echo ";";
$other->put("5");echo $other->read();echo ";";echo $object->read();
'''

PROTECTED_SOURCE_EXPECTED = (
    b'Cannot access protected property ProtectedGrand71::$value|'
    b'Typed property ProtectedA71::$value must not be accessed before initialization|'
    b'Cannot access protected property ProtectedB71::$value|'
    b'1:124;'
    b'125;'
    b'124'
)

CASES = {
    'private-consumer-key-short-write-and-get-owner-abort': (SOURCE, SOURCE_EXPECTED),
    'protected-consumer-key-scope-and-uninitialized-block-pair': (PROTECTED_SOURCE, PROTECTED_SOURCE_EXPECTED),
}

CONTROLS = {
    'raw-class-nonpublic-pair-remains-unsupported':
        (b'<?php\nclass NonpublicClassControl71 {private int $value=3 {get => $this->value;set => $value+10;}}\necho "X";\n', b''),
    'virtual-nonpublic-trait-pair-remains-unsupported':
        (b'<?php\ntrait NonpublicVirtualControl71 {private int $value {get => 700;set {}}}\nclass NonpublicVirtualConsumer71 {use NonpublicVirtualControl71;}\necho "X";\n', b''),
    'nonpublic-asymmetric-combination-remains-unsupported':
        (b'<?php\ntrait NonpublicAsymmetricControl71 {protected private(set) int $value=3 {get => $this->value;set => $value+10;}}\nclass NonpublicAsymmetricConsumer71 {use NonpublicAsymmetricControl71;}\necho "X";\n', b''),
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
