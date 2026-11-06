#!/usr/bin/env python3
"""Physical short SET then GET preserves real roles, compilation order and getter owners."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
$n=0;
function read60($backing){
    global $n;
    $n=$n+1;echo "G";echo $backing;echo ";";
    if($n===1){unset($GLOBALS['object']);echo "U";throw new Exception("gone");}
    if($n===4){echo "R";return "bad";}
    return $backing+100;
}
class SetFirstHookPair60 {
    public int $value=3 {
        set(int|string $supplied) => $supplied+10;
        get => read60($this->value);
    }
    public function __destruct(){echo "D";}
}
$object=new SetFirstHookPair60;$result="keep";
try{$result=$object->value;}catch(Exception $error){echo "C";echo $result==="keep";echo ";";}
unset($error);
$object=new SetFirstHookPair60;
$result=($object->value="5");echo $result==="5";echo ";";echo $object->value;echo ";";
$result=($object->value="2");echo $result==="2";echo ";";echo $object->value;echo ";";
$result="keep";
try{$result=$object->value;}catch(TypeError $error){echo "T";echo $result==="keep";echo ";";}
unset($error);
$result=$object->value;echo $result;echo ";";
unset($object);echo $n;echo "Z";
'''

PURE_ABSENT_SOURCE = b'''<?php
function peek60($backing){echo "K";echo $backing;return $backing;}
class PureSetFirstPair60 {
    public int $value {
        set(int|string $supplied) => $supplied==="peek" ? peek60($this->value) : $supplied+10;
        get => 700;
    }
}
$object=new PureSetFirstPair60;echo $object->value;
try{$object->value="peek";}catch(Error $error){echo $error->getMessage();echo "|";}
$result=($object->value="5");echo $result==="5";echo $object->value;
$result=($object->value="peek");echo $result==="peek";
$result=($object->value="2");echo $result==="2";echo $object->value;
$result=($object->value="peek");echo $result==="peek";
'''

CASES = {
    'class-set-first-block-get-implicit-short-set-crossed-backing':
        (b'<?php class SetFirstBlockPair60 {public int $value=3 '
         b'{set => $value+$this->value+10;'
         b'get {echo "G";$this->value=$this->value+1;return $this->value+100;}}} '
         b'$object=new SetFirstBlockPair60;$result=($object->value=5);'
         b'echo $result;echo $object->value;$result=($object->value=2);'
         b'echo $result;echo $object->value;', b'5G1192G132'),
    'class-set-first-pure-initialized-expression-get-backing-certificate':
        (b'<?php class SetFirstPurePair60 {public int $value=3 '
         b'{set => $value+10;get => 700;}} '
         b'$object=new SetFirstPurePair60;echo $object->value;'
         b'$result=($object->value=5);echo $result;echo $object->value;', b'7005700'),
    'class-set-first-pure-absent-expression-get-uninitialized-and-persistent-backing':
        (PURE_ABSENT_SOURCE, b'700Typed property PureSetFirstPair60::$value must not be accessed before initialization|1700K1511700K121'),
    'class-set-first-expression-get-throw-return-type-retry-and-receiver':
        (SOURCE, b'G3;UDC1;1;G15;115;1;G12;112;G12;RT1;G12;112;D5Z'),
    'class-set-first-expression-get-immediate-closure-class-owner':
        (b'<?php class SetFirstClosurePair60 {public int $value=0 '
         b'{set => $value+10;get => (function(){echo __CLASS__;return 700;})();}} '
         b'$object=new SetFirstClosurePair60;echo $object->value;'
         b'$result=($object->value=5);echo $result;echo $object->value;',
         b'SetFirstClosurePair607005SetFirstClosurePair60700'),
    'first-short-set-variance-error-before-later-get-body-error':
        (b'<?php echo "P";\nclass SetFirstVariancePriority60 {\n public int $value=0 {\n'
         b'  set(string $supplied) => $supplied;\n  get => ($this=1);\n }\n}\necho "Z";', b''),
    'first-short-set-body-error-before-later-get-body-error':
        (b'<?php echo "P";\nclass SetFirstBodyPriority60 {\n public int $value=0 {\n'
         b'  set(int|string $supplied) => ($this=1);\n  get => ($this=2);\n }\n}\necho "Z";', b''),
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
    for name in ['first-short-set-variance-error-before-later-get-body-error',
                 'first-short-set-body-error-before-later-get-body-error']:
        ticks.STATUSES[name], ticks.EXITS[name] = 'static_rejection', 255
    ticks.main(model_timeout=180)


if __name__ == '__main__':
    main()
