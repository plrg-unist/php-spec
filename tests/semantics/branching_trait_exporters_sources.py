#!/usr/bin/env python3
"""Property-specific Trait exporters retain immediate identities and diamond conflicts."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
$n=0;
function rewrite66($supplied,$backing){
    global $n;$n=$n+1;
    echo "H";echo $supplied;echo ":";echo $backing;echo ";";
    if($n===2){unset($GLOBALS['object']);echo "U";throw new Exception("gone");}
    return $backing+$supplied+10;
}
trait LeftPair66 {
    public int $left=3 {
        set(int $supplied){
            echo __TRAIT__,":",__CLASS__,":",static::class,":",__METHOD__,";";
            $next=rewrite66($supplied,$this->left);
            $this->left=$next;
        }
        get => $this->left+100;
    }
}
trait RightPair66 {
    public int $right=7 {
        get => $this->right+1000;
        set(int|string $entry){
            echo __TRAIT__,":",__CLASS__,":",__METHOD__,":",($entry==="4"),":",$entry,":",$this->right,";";
            $this->right=(int)$entry+20;
        }
    }
}
trait JoinedPairs66 {use LeftPair66,RightPair66;}
class ConsumerA66 {use JoinedPairs66;public function __destruct(){echo "A";}}
class ConsumerB66 {use LeftPair66,RightPair66;public function __destruct(){echo "B";}}
$object=new ConsumerA66;$other=new ConsumerB66;
echo $object->left;echo "/";echo $other->right;echo ";";
$result=($object->left="5");echo $result==="5";echo ";";
$rightResult=($object->right="4");echo $rightResult==="4";echo ";";
echo $object->left;echo ":";echo $object->right;echo "/";echo $other->left;echo ";";
try{$object->left=[];}catch(TypeError $error){echo "T";}
unset($error);
try{$result=($object->left="8");}catch(Exception $error){echo "C";echo $result==="5";echo ";";}
unset($error);
$result=($other->left="4");echo $result==="4";echo ";";echo $other->left;echo ";";
$rightResult=($other->right="6");echo $rightResult==="6";echo ";";echo $other->right;echo ";";
$object=new ConsumerA66;
$result=($object->left="2");echo $result==="2";echo ";";echo $object->left;echo ":";echo $object->right;echo ";";
unset($object);unset($other);echo $n;echo "Z";
'''

LEFT_A = b'LeftPair66:ConsumerA66:ConsumerA66:LeftPair66::$left::set;'
LEFT_B = b'LeftPair66:ConsumerB66:ConsumerB66:LeftPair66::$left::set;'
RIGHT_A = b'RightPair66:ConsumerA66:RightPair66::$right::set:1:4:7;'
RIGHT_B = b'RightPair66:ConsumerB66:RightPair66::$right::set::6:7;'
UNINITIALIZED = b'Typed property MixedConsumer66::$second must not be accessed before initialization|'
CASES = {
    'property-specific-joined-and-direct-consumers-with-independent-storage-and-abort':
        (SOURCE, b'103/1007;'+LEFT_A+b'H5:3;1;'+RIGHT_A+b'1;118:1024/103;T'
         +LEFT_A+b'H8:18;UAC1;'+LEFT_B+b'H4:3;1;117;'+RIGHT_B+b'1;1026;'
         +LEFT_A+b'H2:3;1;115:1007;AB4Z'),
    'branching-pure-and-absent-properties-select-their-own-exporter':
        (b'<?php trait PureLeaf66 {public int $first=3 {get => 700;'
         b'set(int|string $entry){$this->first=(int)$entry+10;}}}'
         b'trait AbsentLeaf66 {public int $second {set {echo "N";echo $value;echo ";";}'
         b'get {return $this->second+100;}}}trait MixedJoin66 {use PureLeaf66,AbsentLeaf66;}'
         b'class MixedConsumer66 {use MixedJoin66;}$object=new MixedConsumer66;'
         b'echo $object->first;echo ";";$result=($object->first="5");echo $result==="5";echo ";";'
         b'$row=(array)$object;echo $row["first"];echo ";";unset($row);'
         b'try{echo $object->second;}catch(Error $error){echo $error->getMessage();echo "|";}'
         b'$result=($object->second="4");echo $result==="4";echo ";";'
         b'try{echo $object->second;}catch(Error $error){echo $error->getMessage();echo "|";}',
         b'700;1;15;'+UNINITIALIZED+b'N4;1;'+UNINITIALIZED),
    'branching-get-iife-keeps-its-own-raw-trait-and-consumer-source':
        (b'<?php trait IifeLeaf66 {public int $value=3 {set(int $entry){$this->value=$entry+10;}'
         b'get => (function(){echo __TRAIT__,":",__CLASS__,";";return 700;})();}}'
         b'trait AuxiliaryLeaf66 {public int $aux=11 {get => $this->aux;set {$this->aux=$value;}}}'
         b'trait IifeJoin66 {use IifeLeaf66,AuxiliaryLeaf66;}trait IifeLayer66 {use IifeJoin66;}'
         b'class IifeConsumer66 {use IifeLayer66;}$object=new IifeConsumer66;'
         b'echo $object->value;echo ";";$result=($object->value="5");echo $result==="5";'
         b'echo ";";echo $object->aux;', b'IifeLeaf66:IifeConsumer66;700;1;11'),
    'diamond-same-raw-leaf-keeps-distinct-exporters-and-conflicts':
        (b'<?php echo "P";\ntrait DiamondLeaf66 {public int $value=3 '
         b'{set(int $entry){$this->value=$entry;}get => $this->value;}}\n'
         b'trait DiamondLeft66 {use DiamondLeaf66;}\ntrait DiamondRight66 {use DiamondLeaf66;}\n'
         b'trait DiamondJoin66 {use DiamondLeft66,DiamondRight66;}\n'
         b'class DiamondConsumer66 {use DiamondJoin66;}echo "Z";', b'P'),
    'diamond-local-property-conflict-wins-before-second-exporter':
        (b'<?php echo "P";\ntrait PriorityLeaf66 {public int $value=3 '
         b'{set(int $entry){$this->value=$entry;}get => $this->value;}}\n'
         b'trait PriorityLeft66 {use PriorityLeaf66;}\ntrait PriorityRight66 {use PriorityLeaf66;}\n'
         b'trait PriorityJoin66 {use PriorityLeft66,PriorityRight66;public int $value=3;}\n'
         b'class PriorityConsumer66 {use PriorityJoin66;}echo "Z";', b'P'),
    'distinct-raw-leaves-with-the-same-name-still-conflict':
        (b'<?php echo "P";\ntrait DistinctLeft66 {public int $value=3 '
         b'{set(int $entry){$this->value=$entry;}get => $this->value;}}\n'
         b'trait DistinctRight66 {public int $value=3 '
         b'{get => $this->value;set(int $entry){$this->value=$entry;}}}\n'
         b'class DistinctConsumer66 {use DistinctLeft66,DistinctRight66;}echo "Z";', b'P'),
}
CONTROLS = {
    'branching-short-set-trait-pair-remains-unsupported':
        (b'<?php trait ShortLeaf66 {public int $value=3 {get => $this->value;set => $value+1;}}'
         b'trait PlainLeaf66 {public int $aux=3;}trait ShortJoin66 {use ShortLeaf66,PlainLeaf66;}'
         b'class ShortConsumer66 {use ShortJoin66;}echo "X";', b''),
    'adapted-multiple-trait-wrapper-remains-unsupported':
        (b'<?php trait AdaptedLeaf66 {public int $value=3 {set(int $entry){$this->value=$entry;}'
         b'get => $this->value;}public function tag(){}}trait PlainLeaf66 {public int $aux=3;}'
         b'trait AdaptedJoin66 {use AdaptedLeaf66,PlainLeaf66 {AdaptedLeaf66::tag as renamed;}}'
         b'class AdaptedConsumer66 {use AdaptedJoin66;}echo "X";', b''),
    'parented-multiple-trait-consumer-remains-unsupported':
        (b'<?php trait ParentLeaf66 {public int $value=3 {set(int $entry){$this->value=$entry;}get => $this->value;}}'
         b'trait PlainLeaf66 {public int $aux=3;}class ParentBase66 {}'
         b'class ParentedConsumer66 extends ParentBase66 {use ParentLeaf66,PlainLeaf66;}echo "X";', b''),
}


def main():
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(Path(__file__).relative_to(ticks.ROOT)): ticks.sha(Path(__file__))}}
    ticks.CASES, ticks.CONTROLS = CASES, CONTROLS
    ticks.STATUSES = {name: 'normal' for name in CASES}
    ticks.EXITS = {name: 0 for name in CASES}
    for name in list(CASES)[3:]:
        ticks.STATUSES[name], ticks.EXITS[name] = 'php_error', 255
    ticks.main(model_timeout=1800)


if __name__ == '__main__':
    main()
