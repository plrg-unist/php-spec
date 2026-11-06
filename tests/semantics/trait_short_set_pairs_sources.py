#!/usr/bin/env python3
"""Imported short SET evaluates raw source then implicitly writes Consumer backing."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
$n=0;
function transform68($entry,$trait,$lexical,$called,$method,$line){
    global $n;$n=$n+1;
    echo $trait,":",$lexical,":",$called,":",$method,":",$line,";";
    echo "H";echo $entry;echo ";";
    if($n===2){unset($GLOBALS['object']);echo "U";throw new Exception("gone");}
    return $entry+10;
}
trait ShortPair68 {
    public int $value=3 {
        set(int $entry) =>
            transform68($entry,__TRAIT__,__CLASS__,static::class,__METHOD__,__LINE__);
        get => 700;
    }
}
trait VirtualSide68 {
    public int $side {
        get => 900;
        set {echo "V";echo $value;echo ";";}
    }
}
trait JoinedPairs68 {use ShortPair68,VirtualSide68;}
class ConsumerA68 {use JoinedPairs68;public function __destruct(){echo "A";}}
class ConsumerB68 {use ShortPair68,VirtualSide68;public function __destruct(){echo "B";}}
$object=new ConsumerA68;$other=new ConsumerB68;
echo $object->value;echo "/";echo $other->value;echo ";";
$shape=(array)$object;echo $shape["value"];echo ";";unset($shape);
$result=($object->value="5");echo $result==="5";echo ";";echo $object->value;echo ";";
$shape=(array)$object;echo $shape["value"];echo ";";unset($shape);
$sideResult=($other->side="4");echo $sideResult==="4";echo ";";echo $other->side;echo ";";
$shape=(array)$other;echo $shape["value"];echo ":";echo !isset($shape["side"]);echo ";";unset($shape);
try{$object->value=[];}catch(TypeError $error){echo "T";}
unset($error);
try{$result=($object->value="8");}catch(Exception $error){echo "C";echo $result==="5";echo ";";}
unset($error);
$result=($other->value="4");echo $result==="4";echo ";";echo $other->value;echo ";";
$shape=(array)$other;echo $shape["value"];echo ";";unset($shape);
$object=new ConsumerA68;
$result=($object->value="2");echo $result==="2";echo ";";echo $object->value;echo ";";
$shape=(array)$object;echo $shape["value"];echo ":";echo $object->side;echo ":";echo !isset($shape["side"]);echo ";";unset($shape);
unset($object);unset($other);echo $n;echo "Z";
'''

MAGIC_A = b'ShortPair68:ConsumerA68:ConsumerA68:ShortPair68::$value::set:13;'
MAGIC_B = b'ShortPair68:ConsumerB68:ConsumerB68:ShortPair68::$value::set:13;'
UNINITIALIZED = b'Typed property AbsentConsumer68::$value must not be accessed before initialization|'
CASES = {
    'imported-raw-rhs-and-implicit-consumer-write-keep-two-receiver-owners':
        (SOURCE, b'700/700;3;'+MAGIC_A+b'H5;1;700;15;V4;1;900;3:1;T'
         +MAGIC_A+b'H8;UAC1;'+MAGIC_B+b'H4;1;700;14;'
         +MAGIC_A+b'H2;1;700;12:900:1;AB4Z'),
    'absent-union-short-set-keeps-uninitialized-backing-until-first-implicit-write':
        (b'<?php function absent_result68($entry,$old){echo "R";if($entry==="bad"){return [];}return $old+(int)$entry;}'
         b'trait AbsentShort68 {public int $value {'
         b'set(int|string $entry) => ($entry==="init" ? 10 : absent_result68($entry,$this->value));get => 700;}}'
         b'trait AbsentWrapper68 {use AbsentShort68;}class AbsentConsumer68 {use AbsentWrapper68;}'
         b'$object=new AbsentConsumer68;$result="keep";echo $object->value;echo ";";'
         b'try{$result=($object->value="2");}catch(Error $error){echo $error->getMessage();echo "|";echo $result==="keep";echo ";";}'
         b'unset($error);$result=($object->value="init");echo $result==="init";echo ";";echo $object->value;echo ";";'
         b'$shape=(array)$object;echo $shape["value"];echo ";";unset($shape);'
         b'$result=($object->value="2");echo $result==="2";echo ";";'
         b'$shape=(array)$object;echo $shape["value"];echo ";";unset($shape);'
         b'try{$result=($object->value=[]);}catch(TypeError $error){echo "I";echo $result==="2";echo ";";}'
         b'unset($error);try{$result=($object->value="bad");}catch(TypeError $error){echo "W";echo $result==="2";echo ";";}'
         b'unset($error);$shape=(array)$object;echo $shape["value"];unset($shape);',
         b'700;'+UNINITIALIZED+b'1;1;700;10;R1;12;I1;RW1;12'),
    'implicit-short-set-keeps-raw-rhs-line-separate-from-implicit-write-line':
        (b'<?php\ntrait ImplicitShort68 {\npublic int $value=1 {\nget {return 700;}\nset =>\n($value===4 ? $value+10 : []);\n}\n}\n'
         b'class ImplicitConsumer68 {use ImplicitShort68;}$object=new ImplicitConsumer68;'
         b'echo $object->value;echo ";";$result=($object->value="4");echo $result==="4";echo ";";'
         b'$shape=(array)$object;echo $shape["value"];echo ";";unset($shape);'
         b'try{$result=($object->value="5");}catch(TypeError $error){echo "T";echo $error->getLine();echo ":";echo $result==="4";echo ";";}'
         b'unset($error);$shape=(array)$object;echo $shape["value"];unset($shape);', b'700;1;14;T5:1;14'),
    'first-short-set-variance-precedes-later-get-body-error':
        (b'<?php echo "P";\ntrait VarianceShort68 {\npublic int $value=3 {\n'
         b'set(string $entry) => 0;\nget {$this=1;return 700;}\n}\n}\n'
         b'class VarianceConsumer68 {use VarianceShort68;}echo "Z";', b''),
    'first-get-body-error-precedes-later-short-set-variance':
        (b'<?php echo "P";\ntrait BodyShort68 {\npublic int $value=3 {\n'
         b'get {$this=1;return 700;}\nset(string $entry) => 0;\n}\n}\n'
         b'class BodyConsumer68 {use BodyShort68;}echo "Z";', b''),
    'short-rhs-body-error-precedes-its-builtin-variance':
        (b'<?php echo "P";\ntrait RhsShort68 {\npublic int $value=3 {\n'
         b'set(string $entry) => ($this=1);\nget => 700;\n}\n}\n'
         b'class RhsConsumer68 {use RhsShort68;}echo "Z";', b''),
    'ordinary-default-typing-precedes-short-hook-body-compilation':
        (b'<?php echo "P";\ntrait DefaultShort68 {\npublic int $value="bad" {\n'
         b'set(int $entry) => ($this=1);\nget => 700;\n}\n}\n'
         b'class DefaultConsumer68 {use DefaultShort68;}echo "Z";', b''),
    'short-set-diamond-retains-real-immediate-exporter-conflict':
        (b'<?php echo "P";\ntrait ShortLeaf68 {public int $value=3 {set(int $entry) => $entry+10;get => 700;}}\n'
         b'trait ShortLeft68 {use ShortLeaf68;}\ntrait ShortRight68 {use ShortLeaf68;}\n'
         b'trait ShortJoin68 {use ShortLeft68,ShortRight68;}\n'
         b'class ShortDiamond68 {use ShortJoin68;}echo "Z";', b'P'),
}
CONTROLS = {
    'sole-short-set-trait-remains-unsupported':
        (b'<?php trait SoleShort68 {public int $value=3 {set => $this->value+1;}}'
         b'class SoleConsumer68 {use SoleShort68;}echo "X";', b''),
    'adapted-short-pair-wrapper-remains-unsupported':
        (b'<?php trait AdaptedShort68 {public int $value=3 {get => 700;set => $value+10;}public function tag(){}}'
         b'trait AdaptedWrapper68 {use AdaptedShort68 {AdaptedShort68::tag as renamed;}}'
         b'class AdaptedConsumer68 {use AdaptedWrapper68;}echo "X";', b''),
    'reference-get-short-set-trait-pair-remains-unsupported':
        (b'<?php trait ReferenceShort68 {public int $value=3 {&get {static $slot=7;return $slot;}set => $value+10;}}'
         b'class ReferenceConsumer68 {use ReferenceShort68;}echo "X";', b''),
    'attributed-short-trait-hook-remains-unsupported':
        (b'<?php trait AttributedShort68 {public int $value=3 {get => 700;#[Missing68] set => $value+10;}}'
         b'class AttributedConsumer68 {use AttributedShort68;}echo "X";', b''),
}


def main():
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(Path(__file__).relative_to(ticks.ROOT)): ticks.sha(Path(__file__))}}
    ticks.CASES, ticks.CONTROLS = CASES, CONTROLS
    ticks.STATUSES = {name: 'normal' for name in CASES}
    ticks.EXITS = {name: 0 for name in CASES}
    for name in list(CASES)[3:7]:
        ticks.STATUSES[name], ticks.EXITS[name] = 'static_rejection', 255
    name = list(CASES)[7]
    ticks.STATUSES[name], ticks.EXITS[name] = 'php_error', 255
    ticks.main(model_timeout=1800)


if __name__ == '__main__':
    main()
