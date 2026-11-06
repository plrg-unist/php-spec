#!/usr/bin/env python3
"""Nested Trait pair export preserves real wrapper rows and flattened Consumer identities."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
$n=0;
function rewrite65($supplied,$backing){
    global $n;$n=$n+1;
    echo "H";echo $supplied;echo ":";echo $backing;echo ";";
    if($n===2){unset($GLOBALS['object']);echo "U";throw new Exception("gone");}
    return $backing+$supplied+10;
}
trait InnerPair65 {
    public int $value=3 {
        set(int $supplied){
            echo __TRAIT__,":",__CLASS__,":",static::class,":",__METHOD__,";";
            $next=rewrite65($supplied,$this->value);
            $this->value=$next;
        }
        get => $this->value+100;
    }
}
trait LayerOne65 {use InnerPair65;}
trait LayerTwo65 {use LayerOne65;}
trait LayerThree65 {use LayerTwo65;}
class ConsumerA65 {use LayerTwo65;public function __destruct(){echo "A";}}
class ConsumerB65 {use LayerThree65;public function __destruct(){echo "B";}}
$object=new ConsumerA65;$other=new ConsumerB65;
echo $object->value;echo "/";echo $other->value;echo ";";
$result=($object->value="5");echo $result==="5";echo ";";
echo $object->value;echo "/";echo $other->value;echo ";";
try{$object->value=[];}catch(TypeError $error){echo "T";}
unset($error);
try{$result=($object->value="8");}catch(Exception $error){echo "C";echo $result==="5";echo ";";}
unset($error);
$result=($other->value="4");echo $result==="4";echo ";";echo $other->value;echo ";";
$object=new ConsumerA65;
$result=($object->value="2");echo $result==="2";echo ";";echo $object->value;echo ";";
unset($object);unset($other);echo $n;echo "Z";
'''

MAGIC_A = b'InnerPair65:ConsumerA65:ConsumerA65:InnerPair65::$value::set;'
MAGIC_B = b'InnerPair65:ConsumerB65:ConsumerB65:InnerPair65::$value::set;'
UNINITIALIZED = b'Typed property AbsentConsumer65::$value must not be accessed before initialization|'
CASES = {
    'nested-two-and-three-wrappers-two-consumers-storage-scope-input-abort-and-retry':
        (SOURCE, b'103/103;'+MAGIC_A+b'H5:3;1;118/103;T'+MAGIC_A+b'H8:18;UAC1;'
         +MAGIC_B+b'H4:3;1;117;'+MAGIC_A+b'H2:3;1;115;AB4Z'),
    'nested-pure-get-and-union-block-set-keep-real-backed-consumer-defaults':
        (b'<?php trait PureInner65 {public int $value=3 '
         b'{get => 700;set(int|string $entry){echo "S";echo $entry==="5";echo ";";'
         b'$this->value=(int)$entry+10;}}}'
         b'trait PureLayer65 {use PureInner65;}trait PureOuter65 {use PureLayer65;}'
         b'class PureConsumerA65 {use PureLayer65;}class PureConsumerB65 {use PureOuter65;}'
         b'$a=new PureConsumerA65;$b=new PureConsumerB65;echo $a->value;echo ";";'
         b'$result=($a->value="5");echo $result==="5";echo ";";echo $a->value;echo ";";'
         b'$row=(array)$a;echo $row["value"];echo ";";unset($row);'
         b'$row=(array)$b;echo $row["value"];unset($row);', b'700;S1;1;700;15;3'),
    'nested-absent-backed-slot-survives-implicit-no-write-set':
        (b'<?php trait AbsentInner65 {public int $value '
         b'{set {echo "N";echo $value;echo ";";}get {return $this->value+100;}}}'
         b'trait AbsentLayer65 {use AbsentInner65;}trait AbsentOuter65 {use AbsentLayer65;}'
         b'class AbsentConsumer65 {use AbsentOuter65;}$object=new AbsentConsumer65;'
         b'try{echo $object->value;}catch(Error $error){echo $error->getMessage();echo "|";}'
         b'$result=($object->value="4");echo $result==="4";echo ";";'
         b'try{echo $object->value;}catch(Error $error){echo $error->getMessage();echo "|";}',
         UNINITIALIZED+b'N4;1;'+UNINITIALIZED),
    'nested-imported-get-iife-keeps-raw-inner-trait-and-consumer-source-owner':
        (b'<?php trait IifeInner65 {public int $value=3 '
         b'{set(int $entry){$this->value=$entry+10;}get => (function(){'
         b'echo __TRAIT__,":",__CLASS__,";";return 700;})();}}'
         b'trait IifeLayer65 {use IifeInner65;}trait IifeOuter65 {use IifeLayer65;}'
         b'class IifeConsumer65 {use IifeOuter65;}$object=new IifeConsumer65;'
         b'echo $object->value;echo ";";$result=($object->value="5");echo $result==="5";',
         b'IifeInner65:IifeConsumer65;700;1'),
    'intermediate-wrapper-hooked-property-conflict-before-consumer':
        (b'<?php echo "P";\ntrait ConflictInner65 {public int $value=3 '
         b'{set(int $entry){$this->value=$entry;}get => $this->value;}}\n'
         b'trait ConflictWrapper65 {use ConflictInner65;public int $value=3;}\n'
         b'class ConflictConsumer65 {use ConflictWrapper65;}echo "Z";', b'P'),
    'consumer-hooked-property-conflict-keeps-immediate-wrapper-name':
        (b'<?php echo "P";\ntrait FinalInner65 {public int $value=3 '
         b'{set(int $entry){$this->value=$entry;}get => $this->value;}}\n'
         b'trait FinalLayer65 {use FinalInner65;}\ntrait FinalWrapper65 {use FinalLayer65;}\n'
         b'class FinalConflictConsumer65 {use FinalWrapper65;public int $value=3;}echo "Z";', b'P'),
}
CONTROLS = {
    'adapted-wrapper-trait-pair-remains-unsupported':
        (b'<?php trait AdaptedInner65 {public int $value=3 {set(int $entry){$this->value=$entry;}get => $this->value;}'
         b'public function tag(){}}trait AdaptedLayer65 {use AdaptedInner65 {tag as renamed;}}'
         b'class AdaptedConsumer65 {use AdaptedLayer65;}echo "X";', b''),
    'parented-nested-pair-consumer-remains-unsupported':
        (b'<?php trait ParentInner65 {public int $value=3 {set(int $entry){$this->value=$entry;}get => $this->value;}}'
         b'trait ParentLayer65 {use ParentInner65;}class ParentBase65 {}'
         b'class ParentedConsumer65 extends ParentBase65 {use ParentLayer65;}echo "X";', b''),
}


def main():
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(Path(__file__).relative_to(ticks.ROOT)): ticks.sha(Path(__file__))}}
    ticks.CASES, ticks.CONTROLS = CASES, CONTROLS
    ticks.STATUSES = {name: 'normal' for name in CASES}
    ticks.EXITS = {name: 0 for name in CASES}
    for name in list(CASES)[4:]:
        ticks.STATUSES[name], ticks.EXITS[name] = 'php_error', 255
    ticks.main(model_timeout=900)


if __name__ == '__main__':
    main()
