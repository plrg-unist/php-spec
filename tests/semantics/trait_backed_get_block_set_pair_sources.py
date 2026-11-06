#!/usr/bin/env python3
"""Direct Trait pairs retain raw partners, typed input and distinct Consumer storage."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
$n=0;
function rewrite64($supplied,$backing){
    global $n;$n=$n+1;
    echo "H";echo $supplied;echo ":";echo $backing;echo ";";
    if($n===2){unset($GLOBALS['object']);echo "U";throw new Exception("gone");}
    return $backing+$supplied+10;
}
trait TraitBackedPair64 {
    public int $value=3 {
        set(int $supplied){
            echo __TRAIT__;echo ":";echo __CLASS__;echo ":";echo static::class;echo ":";echo __METHOD__;echo ";";
            $next=rewrite64($supplied,$this->value);
            $this->value=$next;
        }
        get => $this->value+100;
    }
}
class ConsumerA64 {use TraitBackedPair64;public function __destruct(){echo "A";}}
class ConsumerB64 {use TraitBackedPair64;public function __destruct(){echo "B";}}
$object=new ConsumerA64;$other=new ConsumerB64;
echo $object->value;echo "/";echo $other->value;echo ";";
$result=($object->value="5");echo $result==="5";echo ";";
echo $object->value;echo "/";echo $other->value;echo ";";
try{$object->value=[];}catch(TypeError $error){echo "T";}
unset($error);
try{$result=($object->value="8");}catch(Exception $error){echo "C";echo $result==="5";echo ";";}
unset($error);
$result=($other->value="4");echo $result==="4";echo ";";echo $other->value;echo ";";
$object=new ConsumerA64;
$result=($object->value="2");echo $result==="2";echo ";";echo $object->value;echo ";";
unset($object);unset($other);echo $n;echo "Z";
'''

MAGIC_A = b'TraitBackedPair64:ConsumerA64:ConsumerA64:TraitBackedPair64::$value::set;'
MAGIC_B = b'TraitBackedPair64:ConsumerB64:ConsumerB64:TraitBackedPair64::$value::set;'
UNINITIALIZED = b'Typed property AbsentConsumer64::$value must not be accessed before initialization|'
CASES = {
    'two-consumers-import-expression-get-and-typed-block-set-with-storage-and-retry':
        (SOURCE, b'103/103;'+MAGIC_A+b'H5:3;1;118/103;T'+MAGIC_A+b'H8:18;UAC1;'
         +MAGIC_B+b'H4:3;1;117;'+MAGIC_A+b'H2:3;1;115;AB4Z'),
    'trait-pure-initialized-get-uses-block-set-backing-and-real-union-input':
        (b'<?php trait PureTraitPair64 {public int $value=3 '
         b'{get => 700;set(int|string $entry){echo "S";echo $entry==="5";echo ";";'
         b'$this->value=(int)$entry+10;}}}'
         b'class PureConsumerA64 {use PureTraitPair64;}class PureConsumerB64 {use PureTraitPair64;}'
         b'$a=new PureConsumerA64;$b=new PureConsumerB64;echo $a->value;echo ";";'
         b'$result=($a->value="5");echo $result==="5";echo ";";echo $a->value;echo ";";'
         b'$row=(array)$a;echo $row["value"];echo ";";unset($row);'
         b'$row=(array)$b;echo $row["value"];unset($row);', b'700;S1;1;700;15;3'),
    'trait-get-backed-absent-slot-remains-uninitialized-after-implicit-no-write-set':
        (b'<?php trait AbsentTraitPair64 {public int $value '
         b'{set {echo "N";echo $value;echo ";";}get {return $this->value+100;}}}'
         b'class AbsentConsumer64 {use AbsentTraitPair64;}$object=new AbsentConsumer64;'
         b'try{echo $object->value;}catch(Error $error){echo $error->getMessage();echo "|";}'
         b'$result=($object->value="4");echo $result==="4";echo ";";'
         b'try{echo $object->value;}catch(Error $error){echo $error->getMessage();echo "|";}',
         UNINITIALIZED+b'N4;1;'+UNINITIALIZED),
    'imported-get-one-iife-keeps-physical-trait-and-consumer-closure-source':
        (b'<?php trait IifeTrait64 {public int $value=3 '
         b'{set(int $entry){$this->value=$entry+10;}get => (function(){'
         b'echo __TRAIT__;echo ":";echo __CLASS__;echo ";";return 700;})();}}'
         b'class IifeConsumer64 {use IifeTrait64;}$object=new IifeConsumer64;'
         b'echo $object->value;echo ";";$result=($object->value="5");echo $result==="5";',
         b'IifeTrait64:IifeConsumer64;700;1'),
    'trait-first-set-builtin-variance-before-get-body-and-consumer-import':
        (b'<?php echo "P";\ntrait TraitVariance64 {\n public int $value=0 {\n'
         b'  set(string $supplied){$this->value=1;}\n  get {$this=1;return $this->value;}\n }\n}\n'
         b'class InvalidConsumer64 {use TraitVariance64;}echo "Z";', b''),
    'trait-first-get-body-before-set-builtin-variance-and-consumer-import':
        (b'<?php echo "P";\ntrait TraitGetBody64 {\n public int $value=0 {\n'
         b'  get {$this=1;return $this->value;}\n  set(string $supplied){$this->value=1;}\n }\n}\n'
         b'class InvalidConsumer64 {use TraitGetBody64;}echo "Z";', b''),
}
CONTROLS = {
}


def main():
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(Path(__file__).relative_to(ticks.ROOT)): ticks.sha(Path(__file__))}}
    ticks.CASES, ticks.CONTROLS = CASES, CONTROLS
    ticks.STATUSES = {name: 'normal' for name in CASES}
    ticks.EXITS = {name: 0 for name in CASES}
    for name in list(CASES)[4:]:
        ticks.STATUSES[name], ticks.EXITS[name] = 'static_rejection', 255
    ticks.main(model_timeout=600)


if __name__ == '__main__':
    main()
