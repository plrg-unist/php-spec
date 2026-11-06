#!/usr/bin/env python3
"""Virtual Trait hook pairs preserve source authority without allocating backing."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
$n=0;
function observe67($supplied){
    global $n;$n=$n+1;
    echo "H";echo $supplied;echo ";";
    if($n===2){unset($GLOBALS['object']);echo "U";throw new Exception("gone");}
    return $supplied+10;
}
trait VirtualPair67 {
    public int $value {
        set(int $supplied){
            echo __TRAIT__,":",__CLASS__,":",static::class,":",__METHOD__,";";
            $next=observe67($supplied);
            echo "N";echo $next;echo ";";
        }
        get => 700;
    }
}
trait SidePair67 {
    public int $side=11 {
        get => $this->side+1000;
        set {$this->side=$value+10;}
    }
}
trait JoinedPairs67 {use VirtualPair67,SidePair67;}
class ConsumerA67 {use JoinedPairs67;public function __destruct(){echo "A";}}
class ConsumerB67 {use VirtualPair67,SidePair67;public function __destruct(){echo "B";}}
$object=new ConsumerA67;$other=new ConsumerB67;
echo $object->value;echo "/";echo $other->side;echo ";";
$shape=(array)$object;echo !isset($shape["value"]);echo ":";echo $shape["side"];echo ";";unset($shape);
$result=($object->value="5");echo $result==="5";echo ";";echo $object->value;echo ";";
$shape=(array)$object;echo !isset($shape["value"]);echo ";";unset($shape);
$sideResult=($other->side="4");echo $sideResult==="4";echo ";";echo $other->side;echo ";";
try{$object->value=[];}catch(TypeError $error){echo "T";}
unset($error);
try{$result=($object->value="8");}catch(Exception $error){echo "C";echo $result==="5";echo ";";}
unset($error);
$result=($other->value="4");echo $result==="4";echo ";";echo $other->value;echo ";";
$object=new ConsumerA67;
$result=($object->value="2");echo $result==="2";echo ";";echo $object->value;echo ":";echo $object->side;echo ";";
$shape=(array)$object;echo !isset($shape["value"]);echo ":";echo $shape["side"];echo ";";unset($shape);
unset($object);unset($other);echo $n;echo "Z";
'''

MAGIC_A = b'VirtualPair67:ConsumerA67:ConsumerA67:VirtualPair67::$value::set;'
MAGIC_B = b'VirtualPair67:ConsumerB67:ConsumerB67:VirtualPair67::$value::set;'
ALIAS_SOURCE = (b'<?php trait AliasVirtual67 {public int $value {get => 700;'
                b'set(int $entry){echo "S";$alias=$this;$alias->value=$entry;echo "X";}}}'
                b'class AliasConsumer67 {use AliasVirtual67;}$object=new AliasConsumer67;$result="keep";'
                b'echo $object->value;echo ";";try{$result=($object->value="4");}'
                b'catch(Error $error){echo $error->getMessage();echo "|";echo $result==="keep";echo ";";}'
                b'unset($error);echo $object->value;echo ";";$shape=(array)$object;echo !$shape;unset($shape);')
CASES = {
    'virtual-imports-omit-value-storage-alongside-a-real-backed-property':
        (SOURCE, b'700/1011;1:11;'+MAGIC_A+b'H5;N15;1;700;1;1;1014;T'
         +MAGIC_A+b'H8;UAC1;'+MAGIC_B+b'H4;N14;1;700;'
         +MAGIC_A+b'H2;N12;1;700:1011;1:11;AB4Z'),
    'block-get-implicit-set-retains-an-actually-empty-property-table':
        (b'<?php trait EmptyVirtual67 {public int $value {get {return 700;}'
         b'set {echo "V";echo $value;echo ";";}}}'
         b'trait EmptyWrapper67 {use EmptyVirtual67;}'
         b'class EmptyConsumer67 {use EmptyWrapper67;}$object=new EmptyConsumer67;'
         b'echo $object->value;echo ";";$shape=(array)$object;echo !$shape;echo ";";unset($shape);'
         b'$result=($object->value="4");echo $result==="4";echo ";";echo $object->value;echo ";";'
         b'$shape=(array)$object;echo !$shape;unset($shape);', b'700;1;V4;1;700;1'),
    'virtual-union-set-and-get-return-type-failure-preserve-original-results':
        (b'<?php trait ReturnVirtual67 {public int $value {get => "bad";'
         b'set(int|string $entry){echo $entry==="4";}}}'
         b'class ReturnConsumer67 {use ReturnVirtual67;}$object=new ReturnConsumer67;'
         b'$result="keep";try{$result=$object->value;}catch(TypeError $error){echo "R";echo $result==="keep";echo ";";}'
         b'unset($error);$result=($object->value="4");echo $result==="4";echo ";";'
         b'$shape=(array)$object;echo !$shape;unset($shape);', b'R1;11;1'),
    'type-valid-virtual-trait-default-fails-after-the-last-hook-end':
        (b'<?php echo "P";\ntrait DefaultVirtual67 {\npublic int $value=0 {\n'
         b'set(int $entry) {}\nget {\nreturn 700;\n}\n}\n}\n'
         b'class DefaultConsumer67 {use DefaultVirtual67;}echo "Z";', b''),
    'first-set-builtin-variance-error-precedes-later-get-body-and-virtual-default':
        (b'<?php echo "P";\ntrait VarianceVirtual67 {\npublic int $value=0 {\n'
         b'set(string $entry) {}\nget {$this=1;return 700;}\n}\n}\n'
         b'class VarianceConsumer67 {use VarianceVirtual67;}echo "Z";', b''),
    'first-get-body-error-precedes-later-set-variance-and-virtual-default':
        (b'<?php echo "P";\ntrait BodyVirtual67 {\npublic int $value=0 {\n'
         b'get {$this=1;return 700;}\nset(string $entry) {}\n}\n}\n'
         b'class BodyConsumer67 {use BodyVirtual67;}echo "Z";', b''),
    'ordinary-default-type-error-precedes-virtual-hook-body-compilation':
        (b'<?php echo "P";\ntrait TypedDefaultVirtual67 {\npublic int $value="bad" {\n'
         b'get {$this=1;return 700;}\nset(int $entry) {}\n}\n}\n'
         b'class TypedDefaultConsumer67 {use TypedDefaultVirtual67;}echo "Z";', b''),
    'virtual-diamond-still-conflicts-with-real-immediate-exporter-names':
        (b'<?php echo "P";\ntrait VirtualLeaf67 {public int $value {set(int $entry){}get => 700;}}\n'
         b'trait VirtualLeft67 {use VirtualLeaf67;}\ntrait VirtualRight67 {use VirtualLeaf67;}\n'
         b'trait VirtualJoin67 {use VirtualLeft67,VirtualRight67;}\n'
         b'class VirtualDiamond67 {use VirtualJoin67;}echo "Z";', b'P'),
    'active-imported-virtual-set-alias-write-errors-without-creating-storage':
        (ALIAS_SOURCE, b'700;SMust not write to virtual property AliasConsumer67::$value|1;700;1'),
}
CONTROLS = {
    'short-set-trait-pair-remains-unsupported':
        (b'<?php trait ShortVirtual67 {public int $value {get => 700;set => $value+1;}}'
         b'class ShortConsumer67 {use ShortVirtual67;}echo "X";', b''),
    'adapted-virtual-pair-wrapper-remains-unsupported':
        (b'<?php trait AdaptedVirtual67 {public int $value {get => 700;set {}}public function tag(){}}'
         b'trait AdaptedWrapper67 {use AdaptedVirtual67 {AdaptedVirtual67::tag as renamed;}}'
         b'class AdaptedConsumer67 {use AdaptedWrapper67;}echo "X";', b''),
    'parented-virtual-pair-consumer-remains-unsupported':
        (b'<?php trait ParentedVirtual67 {public int $value {get => 700;set {}}}'
         b'class ParentBase67 {}class ParentedConsumer67 extends ParentBase67 {use ParentedVirtual67;}echo "X";', b''),
    'reference-get-virtual-trait-pair-remains-unsupported':
        (b'<?php trait ReferenceVirtual67 {public int $value {&get {static $slot=7;return $slot;}set {}}}'
         b'class ReferenceConsumer67 {use ReferenceVirtual67;}echo "X";', b''),
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
