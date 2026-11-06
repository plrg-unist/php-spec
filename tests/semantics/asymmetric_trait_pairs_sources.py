#!/usr/bin/env python3
"""Consumer-scoped asymmetric backed Trait pairs reuse ordinary permission laws."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
$n=0;
function rewrite70($entry,$base,$trait,$lexical,$called,$method){
    global $n;$n=$n+1;
    echo $trait,":",$lexical,":",$called,":",$method,":",$base,";H";echo $entry;echo ";";
    if($n===3){unset($GLOBALS['object']);echo "U";throw new Exception("gone");}
    return $entry+$base;
}
function deniedInput70(){echo "R";return [];}
function throwingInput70(){echo "Q";throw new Exception("rhs");}
trait ProtectedPair70 {
    public protected(set) int $value=3 {
        set(int $entry) => rewrite70($entry,$this->value,__TRAIT__,__CLASS__,static::class,__METHOD__);
        get => 700;
    }
}
trait PrivatePair70 {
    public private(set) int $secret {
        get {return $this->secret+1000;}
        set(int|string $entry){
            echo __TRAIT__,":",__CLASS__,":",static::class,":",($entry==="4"),";P";
            $this->secret=$entry+20;
        }
    }
}
trait JoinedPairs70 {use ProtectedPair70,PrivatePair70;}
class ConsumerA70 {
    use JoinedPairs70;
    public function writeProtected($entry){return ($this->value=$entry);}
    public function writePrivate($entry){return ($this->secret=$entry);}
    public function writeOtherProtected($other,$entry){return ($other->value=$entry);}
    public function writeOtherPrivate($other,$entry){return ($other->secret=$entry);}
    public function __destruct(){echo "A";}
}
class ConsumerB70 {
    use ProtectedPair70,PrivatePair70;
    public function writeProtected($entry){return ($this->value=$entry);}
    public function writePrivate($entry){return ($this->secret=$entry);}
    public function __destruct(){echo "B";}
}
class GrandA70 extends ConsumerA70 {
    public function ownProtected($entry){return ($this->value=$entry);}
    public function ownPrivate($entry){return ($this->secret=$entry);}
}
$object=new GrandA70;$other=new ConsumerB70;
echo $object->value;echo "/";echo $other->value;echo ";";
try{echo $object->secret;}catch(Error $error){echo $error->getMessage();echo "|";}
unset($error);
$result=$object->writeProtected("5");echo $result==="5";echo ";";
$secretResult=$object->writePrivate("4");echo $secretResult==="4";echo ":";echo $object->secret;echo ";";
$result=$object->ownProtected("6");echo $result==="6";echo ";";
try{$result=($object->value=deniedInput70());}catch(TypeError $error){echo "BAD";}catch(Error $error){echo $error->getMessage();echo "|";}
unset($error);
try{$result=($object->value=throwingInput70());}catch(Exception $error){echo "C";echo $result==="6";echo ";";}
unset($error);
try{$object->ownPrivate("6");}catch(Error $error){echo $error->getMessage();echo "|";}
unset($error);
try{$object->writeOtherProtected($other,"4");}catch(Error $error){echo $error->getMessage();echo "|";}
unset($error);
try{$object->writeOtherPrivate($other,"4");}catch(Error $error){echo $error->getMessage();echo "|";}
unset($error);
try{$object->ownProtected([]);}catch(TypeError $error){echo "T";}
unset($error);
try{$object->writePrivate([]);}catch(TypeError $error){echo "T";}
unset($error);
$shape=(array)$object;echo $shape["value"];echo ":";echo $shape["secret"];echo ":";echo $object->value;echo ";";unset($shape);
$secretResult=$other->writePrivate("7");echo $secretResult==="7";echo ":";echo $other->secret;echo ";";
try{$result=$object->writeProtected("8");}catch(Exception $error){echo "C";echo $result==="6";echo ";";}
unset($error);
$result=$other->writeProtected("4");echo $result==="4";echo ";";
$object=new GrandA70;
$result=$object->writeProtected("2");echo $result==="2";echo ";";
$shape=(array)$object;echo $shape["value"];echo ":";echo $object->value;echo ";";unset($shape);
unset($object);unset($other);echo $n;echo "Z";
'''

EXPECTED = (
    b'700/700;'
    b'Typed property ConsumerA70::$secret must not be accessed before initialization|'
    b'ProtectedPair70:ConsumerA70:GrandA70:ProtectedPair70::$value::set:3;'
    b'H5;'
    b'1;'
    b'PrivatePair70:ConsumerA70:GrandA70:1;'
    b'P1:1024;'
    b'ProtectedPair70:ConsumerA70:GrandA70:ProtectedPair70::$value::set:8;'
    b'H6;'
    b'1;'
    b'RCannot modify protected(set) property ConsumerA70::$value from global scope|'
    b'QC1;'
    b'Cannot modify private(set) property ConsumerA70::$secret from scope GrandA70|'
    b'Cannot modify protected(set) property ConsumerB70::$value from scope GrandA70|'
    b'Cannot modify private(set) property ConsumerB70::$secret from scope GrandA70|'
    b'TT14:24:700;'
    b'PrivatePair70:ConsumerB70:ConsumerB70:;'
    b'P1:1027;'
    b'ProtectedPair70:ConsumerA70:GrandA70:ProtectedPair70::$value::set:14;'
    b'H8;'
    b'UAC1;'
    b'ProtectedPair70:ConsumerB70:ConsumerB70:ProtectedPair70::$value::set:3;'
    b'H4;'
    b'1;'
    b'ProtectedPair70:ConsumerA70:GrandA70:ProtectedPair70::$value::set:3;'
    b'H2;'
    b'1;'
    b'5:700;'
    b'AB5Z'
)

CASES = {
    'consumer-scoped-asymmetric-pairs-preserve-effects-storage-and-owners': (SOURCE, EXPECTED),
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
