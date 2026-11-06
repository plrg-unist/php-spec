#!/usr/bin/env python3
"""Source-backed block SET composes actual hook roles and preserves input and receiver owners."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
$n=0;
function rewrite61($supplied,$backing){
    global $n;
    $n=$n+1;echo "S";echo $supplied;echo ":";echo $backing;echo ";";
    if($n===2){throw new Exception("stop");}
    if($n===4){unset($GLOBALS['object']);echo "U";throw new Exception("gone");}
    return $supplied+$backing+10;
}
class BlockSetHookPair61 {
    public int $value=3 {
        set(int|string $supplied) {
            $next=rewrite61($supplied,$this->value);
            $this->value=$next;
        }
        get => $this->value+100;
    }
    public function __destruct(){echo "D";}
}
$object=new BlockSetHookPair61;
$result=($object->value="4");echo $result==="4";echo ";";echo $object->value;echo ";";
try{$object->value="9";}catch(Exception $error){echo "C";echo $object->value;echo ";";}
unset($error);
$result=($object->value="2");echo $result==="2";echo ";";echo $object->value;echo ";";
try{$object->value="8";}catch(Exception $error){echo "C";echo ";";}
unset($error);
$object=new BlockSetHookPair61;
$result=($object->value="1");echo $result==="1";echo ";";echo $object->value;echo ";";
unset($object);echo $n;echo "Z";
'''

ABSENT_SOURCE = b'''<?php
function peek61($backing){echo "K";echo $backing;return $backing;}
class AbsentBlockPair61 {
    public int $value {
        set(int|string $supplied) {
            $next=$supplied==="peek" ? peek61($this->value) : $supplied+10;
            $this->value=$next;
        }
        get => 700;
    }
}
$object=new AbsentBlockPair61;echo $object->value;
try{$object->value="peek";}catch(Error $error){echo $error->getMessage();echo "|";}
$result=($object->value="5");echo $result==="5";echo $object->value;
$result=($object->value="peek");echo $result==="peek";
$result=($object->value="2");echo $result==="2";echo $object->value;
$result=($object->value="peek");echo $result==="peek";
'''

CASES = {
    'class-get-first-expression-get-explicit-backed-block-set':
        (b'<?php class GetFirstBlockPair61 {public int $value=3 '
         b'{get => $this->value+100;set(int|string $incoming){$this->value=$incoming+10;}}} '
         b'$object=new GetFirstBlockPair61;$result=($object->value="5");'
         b'echo $result==="5";echo $object->value;', b'1115'),
    'class-set-first-backed-block-get-implicit-block-set':
        (b'<?php class ReversedBlocks61 {public int $value=3 '
         b'{set {$this->value=$value+$this->value+10;}'
         b'get {echo "G";$this->value=$this->value+1;return $this->value+100;}}} '
         b'$object=new ReversedBlocks61;$result=($object->value=5);'
         b'echo $result;echo $object->value;$result=($object->value=2);'
         b'echo $result;echo $object->value;', b'5G1192G132'),
    'class-pure-initialized-block-and-expression-get-use-actual-backed-set':
        (b'<?php class PureBlockPair61 {public int $value=3 '
         b'{get {return 700;}set {$this->value=$value+10;}}} '
         b'class PureExpressionBlockPair61 {public int $value=4 '
         b'{set {$this->value=$value+20;}get => 800;}} '
         b'$first=new PureBlockPair61;echo $first->value;echo ($first->value=5);echo $first->value;'
         b'$second=new PureExpressionBlockPair61;echo $second->value;echo ($second->value=2);echo $second->value;',
         b'70057008002800'),
    'class-absent-pure-get-backed-block-set-uninitialized-read-and-first-write':
        (ABSENT_SOURCE, b'700Typed property AbsentBlockPair61::$value must not be accessed before initialization|1700K1511700K121'),
    'class-typed-block-set-statement-input-storage-throw-retry-and-receiver':
        (SOURCE, b'S4:3;1;117;S9:17;C117;S2:17;1;129;S8:29;UDC;S1:3;1;114;D5Z'),
    'first-block-set-variance-error-before-later-get-body-error':
        (b'<?php echo "P";\nclass BlockSetVariancePriority61 {\n public int $value=0 {\n'
         b'  set(string $supplied){$this->value=$supplied;}\n  get => ($this=1);\n }\n}\necho "Z";', b''),
    'first-get-body-error-before-later-block-set-variance-error':
        (b'<?php echo "P";\nclass GetBeforeBlockVariance61 {\n public int $value=0 {\n'
         b'  get => ($this=1);\n  set(string $supplied){$this->value=$supplied;}\n }\n}\necho "Z";', b''),
}
CONTROLS = {
    'trait-explicit-backed-block-set-pair-remains-unsupported':
        (b'<?php trait BlockSetTrait61 {public int $value=3 '
         b'{get => 700;set(int|string $supplied){$this->value=$supplied+10;}}} '
         b'class BlockSetConsumer61 {use BlockSetTrait61;}echo "X";', b''),
}


def main():
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(Path(__file__).relative_to(ticks.ROOT)): ticks.sha(Path(__file__))}}
    ticks.CASES, ticks.CONTROLS = CASES, CONTROLS
    ticks.STATUSES = {name: 'normal' for name in CASES}
    ticks.EXITS = {name: 0 for name in CASES}
    for name in ['first-block-set-variance-error-before-later-get-body-error',
                 'first-get-body-error-before-later-block-set-variance-error']:
        ticks.STATUSES[name], ticks.EXITS[name] = 'static_rejection', 255
    ticks.main(model_timeout=180)


if __name__ == '__main__':
    main()
