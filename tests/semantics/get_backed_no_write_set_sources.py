#!/usr/bin/env python3
"""GET syntax supplies real backing while a block SET body performs no backing write."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
$n=0;
function log62($supplied){
    global $n;
    $n=$n+1;echo "S";echo $supplied;echo ";";
    if($n===2){unset($GLOBALS['object']);echo "U";throw new Exception("gone");}
}
class GetBackedNoWrite62 {
    public int $value {
        set {log62($value);}
        get => $this->value+100;
    }
    public function __destruct(){echo "D";}
}
$object=new GetBackedNoWrite62;
try{echo $object->value;}catch(Error $error){echo $error->getMessage();echo "|";}
unset($error);
$result=($object->value="4");echo $result==="4";echo ";";
try{echo $object->value;}catch(Error $error){echo $error->getMessage();echo "|";}
unset($error);
try{$result=($object->value="8");}catch(Exception $error){echo "C";echo $result==="4";echo ";";}
unset($error);
$object=new GetBackedNoWrite62;
$result=($object->value="5");echo $result==="5";echo ";";
try{echo $object->value;}catch(Error $error){echo $error->getMessage();echo "|";}
unset($error);unset($object);echo $n;echo "Z";
'''
UNINITIALIZED = b'Typed property GetBackedNoWrite62::$value must not be accessed before initialization|'

CASES = {
    'class-initialized-get-backing-explicit-no-write-set-input-and-storage':
        (b'<?php class ExplicitNoWrite62 {public int $value=3 '
         b'{get => $this->value+100;set(int|string $supplied){'
         b'echo "E";echo $supplied==="5";echo ":";echo $supplied;echo ";";}}} '
         b'$object=new ExplicitNoWrite62;echo $object->value;echo ";";'
         b'$result=($object->value="5");echo $result==="5";echo ";";echo $object->value;echo ";";'
         b'try{$object->value=[];}catch(TypeError $error){echo "T";}echo $object->value;',
         b'103;E1:5;1;103;T103'),
    'class-block-get-initializes-and-increments-while-implicit-set-never-writes':
        (b'<?php class BlockGetNoWrite62 {public int $value=3 '
         b'{set {echo "S";echo $value;echo ";";}'
         b'get {$this->value=$this->value+1;return $this->value+100;}}} '
         b'$object=new BlockGetNoWrite62;echo $object->value;echo ";";'
         b'$result=($object->value=20);echo $result;echo ";";echo $object->value;echo ";";',
         b'104;S20;20;105;'),
    'class-absent-get-backed-no-write-set-never-initializes-and-keeps-receiver':
        (SOURCE, UNINITIALIZED+b'S4;1;'+UNINITIALIZED+b'S8;UDC1;S5;1;'+UNINITIALIZED+b'D3Z'),
    'first-no-write-set-variance-before-later-backed-get-body-error':
        (b'<?php echo "P";\nclass NoWriteVarianceFirst62 {\n public int $value=0 {\n'
         b'  set(string $supplied){echo $supplied;}\n  get {$this=1;return $this->value;}\n }\n}\necho "Z";', b''),
    'first-backed-get-body-error-before-later-no-write-set-variance':
        (b'<?php echo "P";\nclass BackedGetBodyFirst62 {\n public int $value=0 {\n'
         b'  get {$this=1;return $this->value;}\n  set(string $supplied){echo $supplied;}\n }\n}\necho "Z";', b''),
}
CONTROLS = {
    'true-virtual-get-and-no-write-set-pair-remains-separate':
        (b'<?php class VirtualNoWrite62 {public int $value '
         b'{get => 700;set {echo "S";}}}echo "X";', b''),
    'trait-get-backed-no-write-set-pair-remains-unsupported':
        (b'<?php trait TraitNoWrite62 {public int $value=3 '
         b'{get => $this->value+100;set {echo "S";}}} '
         b'class TraitNoWriteConsumer62 {use TraitNoWrite62;}echo "X";', b''),
}


def main():
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(Path(__file__).relative_to(ticks.ROOT)): ticks.sha(Path(__file__))}}
    ticks.CASES, ticks.CONTROLS = CASES, CONTROLS
    ticks.STATUSES = {name: 'normal' for name in CASES}
    ticks.EXITS = {name: 0 for name in CASES}
    for name in ['first-no-write-set-variance-before-later-backed-get-body-error',
                 'first-backed-get-body-error-before-later-no-write-set-variance']:
        ticks.STATUSES[name], ticks.EXITS[name] = 'static_rejection', 255
    ticks.main(model_timeout=180)


if __name__ == '__main__':
    main()
