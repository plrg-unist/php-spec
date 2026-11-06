#!/usr/bin/env python3
"""Consumer-scoped asymmetric backed Trait pairs reuse ordinary permission laws."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
$n=0;
function protected70($entry,$base,$lexical,$called){
    global $n;$n=$n+1;
    echo "H",$entry,":",$base,":",$lexical,":",$called,";";
    if($n===2){unset($GLOBALS['object']);echo "U";throw new Exception("gone");}
    return $entry+$base;
}
function denied70(){echo "R";return [];}
function throwing70(){echo "Q";throw new Exception("rhs");}
trait ProtectedPair70 {
    public protected(set) int $value=3 {
        set(int $entry) => protected70($entry,$this->value,__CLASS__,static::class);
        get => 700;
    }
}
trait ProtectedWrapper70 {use ProtectedPair70;}
class ConsumerA70 {
    use ProtectedWrapper70;
    public function put($entry){return ($this->value=$entry);}
    public function other($target,$entry){return ($target->value=$entry);}
    public function __destruct(){echo "A";}
}
class ConsumerB70 {
    use ProtectedPair70;
    public function put($entry){return ($this->value=$entry);}
    public function __destruct(){echo "B";}
}
class GrandA70 extends ConsumerA70 {public function own($entry){return ($this->value=$entry);}}
$object=new GrandA70;$other=new ConsumerB70;
$result=$object->own("5");echo $result==="5";echo ":";echo $object->value;echo ";";
try{$result=($object->value=denied70());}catch(TypeError $error){echo "BAD";}catch(Error $error){echo $error->getMessage();echo "|";}
unset($error);
try{$result=($object->value=throwing70());}catch(Exception $error){echo "C";echo $result==="5";echo ";";}
unset($error);
try{$object->other($other,"4");}catch(Error $error){echo $error->getMessage();echo "|";}
unset($error);
try{$object->own([]);}catch(TypeError $error){echo "T";}
unset($error);
$shape=(array)$object;echo $shape["value"];echo ";";unset($shape);
try{$result=$object->put("8");}catch(Exception $error){echo "C";echo $result==="5";echo ";";}
unset($error);
$result=$other->put("4");echo $result==="4";echo ";";
$object=new GrandA70;$result=$object->put("2");echo $result==="2";echo ";";
$shape=(array)$object;echo $shape["value"];echo ":";echo $object->value;echo ";";unset($shape);
unset($object);unset($other);echo $n;echo "Z";
'''

SOURCE_EXPECTED = (
    b'H5:3:ConsumerA70:GrandA70;'
    b'1:700;'
    b'RCannot modify protected(set) property ConsumerA70::$value from global scope|'
    b'QC1;'
    b'Cannot modify protected(set) property ConsumerB70::$value from scope GrandA70|'
    b'T8;'
    b'H8:8:ConsumerA70:GrandA70;'
    b'UAC1;'
    b'H4:3:ConsumerB70:ConsumerB70;'
    b'1;'
    b'H2:3:ConsumerA70:GrandA70;'
    b'1;'
    b'5:700;'
    b'AB4Z'
)

PRIVATE_SOURCE = b'''<?php
trait PrivatePair70 {
    public private(set) int $secret {
        get {return $this->secret+1000;}
        set(int|string $entry){echo "P";echo $entry==="4";$this->secret=$entry+20;}
    }
}
class PrivateA70 {
    use PrivatePair70;
    public function put($entry){return ($this->secret=$entry);}
    public function other($target,$entry){return ($target->secret=$entry);}
}
class PrivateB70 {use PrivatePair70;public function put($entry){return ($this->secret=$entry);}}
class PrivateGrand70 extends PrivateA70 {public function own($entry){return ($this->secret=$entry);}}
$object=new PrivateGrand70;$other=new PrivateB70;
try{echo $object->secret;}catch(Error $error){echo $error->getMessage();echo "|";}
unset($error);
$result=$object->put("4");echo $result==="4";echo ":";echo $object->secret;echo ";";
try{$object->own("6");}catch(Error $error){echo $error->getMessage();echo "|";}
unset($error);
try{$object->other($other,[]);}catch(TypeError $error){echo "BAD";}catch(Error $error){echo $error->getMessage();echo "|";}
unset($error);
try{$object->put([]);}catch(TypeError $error){echo "T";}
unset($error);
$result=$other->put("7");echo $result==="7";echo ":";echo $other->secret;echo ";";echo $object->secret;
'''

PRIVATE_SOURCE_EXPECTED = (
    b'Typed property PrivateA70::$secret must not be accessed before initialization|'
    b'P11:1024;'
    b'Cannot modify private(set) property PrivateA70::$secret from scope PrivateGrand70|'
    b'Cannot modify private(set) property PrivateB70::$secret from scope PrivateGrand70|'
    b'TP1:1027;'
    b'1024'
)

CASES = {
    'protected-consumer-permission-rhs-priority-and-owner-abort': (SOURCE, SOURCE_EXPECTED),
    'private-consumer-scope-uninitialized-storage-and-reception': (PRIVATE_SOURCE, PRIVATE_SOURCE_EXPECTED),
    'private-set-pair-finality-fails-after-main-at-child-link':
        (b'<?php\necho "P";\ntrait PrivateFinalPair70 {\n    public private(set) int $value=3 {\n        set(int $entry) => $entry+10;\n        get => 700;\n    }\n}\nclass FinalConsumer70 {use PrivateFinalPair70;}\nif(true){class RedeclaringChild70 extends FinalConsumer70 {public int $value=3;}}\necho "X";\n', b'P'),
}

CONTROLS = {
    'virtual-asymmetric-trait-pair-remains-unsupported':
        (b'<?php\ntrait VirtualAsymmetricControl70 {public protected(set) int $value {get => 700;set {echo "S";}}}\nclass VirtualAsymmetricConsumer70 {use VirtualAsymmetricControl70;}\necho "X";\n', b''),
    'explicit-final-trait-pair-remains-unsupported':
        (b'<?php\ntrait ExplicitFinalControl70 {final public int $value=3 {get => 700;set => $value+10;}}\nclass ExplicitFinalConsumer70 {use ExplicitFinalControl70;}\necho "X";\n', b''),
    'class-asymmetric-pair-remains-unsupported':
        (b'<?php\nclass ClassAsymmetricControl70 {public protected(set) int $value=3 {get => 700;set => $value+10;}}\necho "X";\n', b''),
}


def main():
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(Path(__file__).relative_to(ticks.ROOT)): ticks.sha(Path(__file__))}}
    ticks.CASES, ticks.CONTROLS = CASES, CONTROLS
    ticks.STATUSES = {name: 'normal' for name in CASES}
    ticks.EXITS = {name: 0 for name in CASES}
    name = 'private-set-pair-finality-fails-after-main-at-child-link'
    ticks.STATUSES[name], ticks.EXITS[name] = 'php_error', 255
    ticks.main(model_timeout=1800)


if __name__ == '__main__':
    main()
