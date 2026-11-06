#!/usr/bin/env python3
"""Disjoint ordinary Parent storage composes with authentic Trait pair Consumers."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
$n=0;
function transform69($entry,$base,$trait,$lexical,$called,$method,$line){
    global $n;$n=$n+1;
    echo $trait,":",$lexical,":",$called,":",$method,":",$line,":",$base,";";
    echo "H";echo $entry;echo ";";
    if($n===2){unset($GLOBALS['object']);echo "U";throw new Exception("gone");}
    return $entry+$base;
}
trait ParentPair69 {
    public int $value=3 {
        set(int $entry) =>
            transform69($entry,$this->base,__TRAIT__,__CLASS__,static::class,__METHOD__,__LINE__);
        get => 700;
    }
}
trait VirtualSide69 {
    public int $side {
        get => 900;
        set {echo "V";echo $value;echo ";";}
    }
}
trait JoinedPairs69 {use ParentPair69,VirtualSide69;}
class OrdinaryBaseA69 {public int $base=13;}
class OrdinaryBaseB69 {public int $base=17;}
class ConsumerA69 extends OrdinaryBaseA69 {use JoinedPairs69;public function __destruct(){echo "A";}}
class ConsumerB69 extends OrdinaryBaseB69 {use ParentPair69,VirtualSide69;public function __destruct(){echo "B";}}
class GrandA69 extends ConsumerA69 {}
$object=new GrandA69;$other=new ConsumerB69;
echo $object->value;echo "/";echo $other->value;echo ";";
$shape=(array)$object;echo $shape["base"];echo ":";echo $shape["value"];echo ":";echo !isset($shape["side"]);echo ";";unset($shape);
$result=($object->value="5");echo $result==="5";echo ";";echo $object->value;echo ";";
$shape=(array)$object;echo $shape["value"];echo ";";unset($shape);
$sideResult=($other->side="4");echo $sideResult==="4";echo ";";echo $other->side;echo ";";
$shape=(array)$other;echo $shape["base"];echo ":";echo $shape["value"];echo ":";echo !isset($shape["side"]);echo ";";unset($shape);
try{$object->value=[];}catch(TypeError $error){echo "T";}
unset($error);
try{$result=($object->value="8");}catch(Exception $error){echo "C";echo $result==="5";echo ";";}
unset($error);
$result=($other->value="4");echo $result==="4";echo ";";echo $other->value;echo ";";
$shape=(array)$other;echo $shape["base"];echo ":";echo $shape["value"];echo ";";unset($shape);
$object=new GrandA69;
$result=($object->value="2");echo $result==="2";echo ";";echo $object->value;echo ";";
$shape=(array)$object;echo $shape["base"];echo ":";echo $shape["value"];echo ":";echo $object->side;echo ":";echo !isset($shape["side"]);echo ";";unset($shape);
unset($object);unset($other);echo $n;echo "Z";
'''

MAGIC_A = b'ParentPair69:ConsumerA69:GrandA69:ParentPair69::$value::set:13:13;'
MAGIC_B = b'ParentPair69:ConsumerB69:ConsumerB69:ParentPair69::$value::set:13:17;'
UNINITIALIZED = b'Typed property BlockConsumer69::$value must not be accessed before initialization|'
CASES = {
    'parented-importer-and-descendant-preserve-parent-storage-scope-and-two-owners':
        (SOURCE, b'700/700;13:3:1;'+MAGIC_A+b'H5;1;700;18;V4;1;900;17:3:1;T'
         +MAGIC_A+b'H8;UAC1;'+MAGIC_B+b'H4;1;700;17:21;'
         +MAGIC_A+b'H2;1;700;13:15:900:1;AB4Z'),
    'parented-block-pair-keeps-real-uninitialized-and-inherited-storage':
        (b'<?php trait BlockPair69 {public int $value {get {return $this->value+100;}'
         b'set {$this->value=$value+$this->base;}}}'
         b'trait BlockWrapper69 {use BlockPair69;}class BlockBase69 {public int $base=10;}'
         b'class BlockConsumer69 extends BlockBase69 {use BlockWrapper69;}'
         b'class BlockGrand69 extends BlockConsumer69 {}$object=new BlockGrand69;'
         b'try{echo $object->value;}catch(Error $error){echo $error->getMessage();echo "|";}'
         b'unset($error);$result=($object->value="4");echo $result==="4";echo ";";echo $object->value;echo ";";'
         b'$shape=(array)$object;echo $shape["base"];echo ":";echo $shape["value"];unset($shape);',
         UNINITIALIZED+b'1;114;10:14'),
    'parented-virtual-pair-keeps-no-value-slot-and-consumer-versus-called-scope':
        (b'<?php trait VirtualPair69 {public int $value {get => 700;'
         b'set(int|string $entry){echo __TRAIT__,":",__CLASS__,":",static::class,":",($entry==="4"),":",$this->base,";";}}}'
         b'class VirtualBase69 {public int $base=17;}'
         b'class VirtualConsumer69 extends VirtualBase69 {use VirtualPair69;}'
         b'class VirtualGrand69 extends VirtualConsumer69 {}$object=new VirtualGrand69;'
         b'echo $object->value;echo ";";$shape=(array)$object;echo $shape["base"];echo ":";echo !isset($shape["value"]);echo ";";unset($shape);'
         b'$result=($object->value="4");echo $result==="4";echo ";";echo $object->value;echo ";";'
         b'try{$object->value=[];}catch(TypeError $error){echo "T";}unset($error);'
         b'$shape=(array)$object;echo $shape["base"];echo ":";echo !isset($shape["value"]);unset($shape);',
         b'700;17:1;VirtualPair69:VirtualConsumer69:VirtualGrand69:1:17;1;700;T17:1'),
    'ordinary-final-parent-fails-after-valid-trait-property-composition':
        (b'<?php echo "P";\nfinal class FinalBase69 {public int $base=13;}\n'
         b'trait FinalPair69 {public int $value=3 {set(int $entry) => $entry+10;get => 700;}}\n'
         b'if(true){class FinalConsumer69 extends FinalBase69 {use FinalPair69;}}echo "Z";', b'P'),
    'trait-property-conflict-precedes-final-parent-link-failure':
        (b'<?php echo "P";\nfinal class ConflictBase69 {public int $base=13;}\n'
         b'trait ConflictLeft69 {public int $value=3 {set(int $entry) => $entry+10;get => 700;}}\n'
         b'trait ConflictRight69 {public int $value=3 {get => 700;set(int $entry) => $entry+10;}}\n'
         b'if(true){class ConflictConsumer69 extends ConflictBase69 {use ConflictLeft69,ConflictRight69;}}echo "Z";', b'P'),
    'raw-trait-body-error-precedes-main-and-final-parent-linking':
        (b'<?php echo "P";\nfinal class BodyBase69 {public int $base=13;}\n'
         b'trait BodyPair69 {public int $value=3 {set(int $entry) => ($this=1);get => 700;}}\n'
         b'if(true){class BodyConsumer69 extends BodyBase69 {use BodyPair69;}}echo "Z";', b''),
}
CONTROLS = {
    'same-name-parent-property-override-remains-unsupported':
        (b'<?php class SameBase69 {public int $value=3;}'
         b'trait SamePair69 {public int $value=3 {set => $value+10;get => 700;}}'
         b'class SameConsumer69 extends SameBase69 {use SamePair69;}echo "X";', b''),
    'disjoint-hooked-parent-remains-unsupported':
        (b'<?php class HookedBase69 {public int $base=13 {get => $this->base;set => $value;}}'
         b'trait HookedPair69 {public int $value=3 {set => $value+10;get => 700;}}'
         b'class HookedConsumer69 extends HookedBase69 {use HookedPair69;}echo "X";', b''),
    'adapted-parented-consumer-remains-unsupported':
        (b'<?php class AdaptedBase69 {public int $base=13;}'
         b'trait AdaptedPair69 {public int $value=3 {set => $value+10;get => 700;}public function tag(){}}'
         b'class AdaptedConsumer69 extends AdaptedBase69 {use AdaptedPair69 {AdaptedPair69::tag as renamed;}}echo "X";', b''),
    'nominal-set-parameter-remains-unsupported':
        (b'<?php class NominalBase69 {public int $base=13;}class NominalInput69 {}'
         b'trait NominalPair69 {public int $value=3 {set(NominalInput69 $entry) => 4;get => 700;}}'
         b'class NominalConsumer69 extends NominalBase69 {use NominalPair69;}echo "X";', b''),
    'reference-get-parented-pair-remains-unsupported':
        (b'<?php class ReferenceBase69 {public int $base=13;}'
         b'trait ReferencePair69 {public int $value=3 {&get {static $slot=7;return $slot;}set => $value+10;}}'
         b'class ReferenceConsumer69 extends ReferenceBase69 {use ReferencePair69;}echo "X";', b''),
    'plain-redeclared-inherited-hook-parent-remains-unsupported':
        (b'<?php class HookRootControl69 {public int $base=13 {get => $this->base+1000;}}'
         b'class OrdinaryLookingControl69 extends HookRootControl69 {public int $base=13;}'
         b'trait HeldPairControl69 {public int $value=3 {get => 700;set => $value+10;}}'
         b'class HeldConsumerControl69 extends OrdinaryLookingControl69 {use HeldPairControl69;}'
         b'$object=new HeldConsumerControl69;echo $object->base;echo ";";echo $object->value;', b''),
}


def main():
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(Path(__file__).relative_to(ticks.ROOT)): ticks.sha(Path(__file__))}}
    ticks.CASES, ticks.CONTROLS = CASES, CONTROLS
    ticks.STATUSES = {name: 'normal' for name in CASES}
    ticks.EXITS = {name: 0 for name in CASES}
    for name in list(CASES)[3:5]:
        ticks.STATUSES[name], ticks.EXITS[name] = 'php_error', 255
    name = list(CASES)[5]
    ticks.STATUSES[name], ticks.EXITS[name] = 'static_rejection', 255
    ticks.main(model_timeout=1800)


if __name__ == '__main__':
    main()
