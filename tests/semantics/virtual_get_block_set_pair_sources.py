#!/usr/bin/env python3
"""True virtual GET/block-SET pairs keep effects and inputs without a property slot."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
$n=0;
function log63($supplied){
    global $n;
    $n=$n+1;echo "S";echo $supplied;echo ";";
    if($n===2){unset($GLOBALS['object']);echo "U";throw new Exception("gone");}
}
class VirtualPair63 {
    public int $value {
        set {log63($value);}
        get => 700;
    }
    public function __destruct(){echo "D";}
}
$object=new VirtualPair63;
echo $object->value;echo ";";echo (array)$object===[];echo ";";
$result=($object->value="4");echo $result==="4";echo ";";
echo $object->value;echo ";";echo (array)$object===[];echo ";";
try{$object->value=[];}catch(TypeError $error){echo "T";}
unset($error);
try{$result=($object->value="8");}catch(Exception $error){echo "C";echo $result==="4";echo ";";}
unset($error);
$object=new VirtualPair63;
$result=($object->value="5");echo $result==="5";echo ";";
echo $object->value;echo ";";echo (array)$object===[];echo ";";
unset($object);echo $n;echo "Z";
'''

CASES = {
    'virtual-set-first-expression-get-no-slot-input-type-abort-and-retry':
        (SOURCE, b'700;1;S4;1;700;1;TS8;UDC1;S5;1;700;1;D3Z'),
    'virtual-get-first-block-explicit-set-and-get-result-type-failure':
        (b'<?php $answer=700;function read63(){global $answer;echo "G";return $answer;}'
         b'class ExplicitVirtual63 {public int $value '
         b'{get {return read63();}set(int|string $supplied){'
         b'echo "E";echo $supplied==="5";echo ":";echo $supplied;echo ";";}}} '
         b'$object=new ExplicitVirtual63;$read=$object->value;echo $read;echo ";";'
         b'$result=($object->value="5");echo $result==="5";echo ";";'
         b'try{$object->value=[];}catch(TypeError $error){echo "T";}'
         b'$answer=[];try{$read=$object->value;}catch(TypeError $error){echo "R";}'
         b'echo $read;echo ";";echo (array)$object===[];',
         b'G700;E1:5;1;TGR700;1'),
    'virtual-default-rejected-after-successful-physical-hooks':
        (b'<?php echo "P";\nclass VirtualDefault63 {\n public int $value=0 {\n'
         b'  set(int $supplied){echo $supplied;}\n  get => 700;\n }\n}\necho "Z";', b''),
    'virtual-default-rejection-uses-last-block-hook-end-line':
        (b'<?php echo "P";\nclass VirtualDefaultEnd63 {\n public int $value=0 {\n'
         b'  get => 700;\n  set {\n   echo $value;\n  }\n }\n}\necho "Z";', b''),
    'virtual-default-loses-to-first-set-builtin-variance-error':
        (b'<?php echo "P";\nclass VirtualVariance63 {\n public int $value=0 {\n'
         b'  set(string $supplied){echo $supplied;}\n  get => 700;\n }\n}\necho "Z";', b''),
    'virtual-default-loses-to-first-get-body-error':
        (b'<?php echo "P";\nclass VirtualBody63 {\n public int $value=0 {\n'
         b'  get {$this=1;return 700;}\n  set {echo $value;}\n }\n}\necho "Z";', b''),
    'ordinary-default-type-error-before-virtual-hook-body-error':
        (b'<?php echo "P";\nclass VirtualDefaultType63 {\n public int $value=[] {\n'
         b'  get {$this=1;return 700;}\n  set {echo $value;}\n }\n}\necho "Z";', b''),
}
CONTROLS = {
    'trait-true-virtual-get-block-set-pair-remains-unsupported':
        (b'<?php trait VirtualTrait63 {public int $value '
         b'{get => 700;set {echo "S";}}}class VirtualConsumer63 {use VirtualTrait63;}echo "X";', b''),
}


def main():
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(Path(__file__).relative_to(ticks.ROOT)): ticks.sha(Path(__file__))}}
    ticks.CASES, ticks.CONTROLS = CASES, CONTROLS
    ticks.STATUSES = {name: 'normal' for name in CASES}
    ticks.EXITS = {name: 0 for name in CASES}
    for name in CASES:
        if name not in list(CASES)[:2]:
            ticks.STATUSES[name], ticks.EXITS[name] = 'static_rejection', 255
    ticks.main(model_timeout=180)


if __name__ == '__main__':
    main()
