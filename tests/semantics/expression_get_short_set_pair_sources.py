#!/usr/bin/env python3
"""Expression GET and short SET share source-backed storage and genuine getter owners."""
from pathlib import Path

import tick_sources as ticks


SOURCE = b'''<?php
$n=0;
function read59($backing){
    global $n;
    $n=$n+1;echo "G";echo $backing;echo ";";
    if($n===1){unset($GLOBALS['object']);echo "U";throw new Exception("gone");}
    if($n===4){echo "R";return "bad";}
    return $backing+100;
}
class ExpressionGetShortSetPair59 {
    public int $value=3 {
        get => read59($this->value);
        set(int|string $supplied) => $supplied+10;
    }
    public function __destruct(){echo "D";}
}
$object=new ExpressionGetShortSetPair59;$result="keep";
try{$result=$object->value;}catch(Exception $error){echo "C";echo $result==="keep";echo ";";}
unset($error);
$object=new ExpressionGetShortSetPair59;
$result=($object->value="5");echo $result==="5";echo ";";echo $object->value;echo ";";
$result=($object->value="2");echo $result==="2";echo ";";echo $object->value;echo ";";
$result="keep";
try{$result=$object->value;}catch(TypeError $error){echo "T";echo $result==="keep";echo ";";}
unset($error);
$result=$object->value;echo $result;echo ";";
unset($object);echo $n;echo "Z";
'''

PURE_ABSENT_SOURCE = b'''<?php
function peek59($backing){echo "K";echo $backing;return $backing;}
class PureExpressionPair59 {
    public int $value {
        get => 700;
        set(int|string $supplied) => $supplied==="peek" ? peek59($this->value) : $supplied+10;
    }
}
$object=new PureExpressionPair59;echo $object->value;
try{$object->value="peek";}catch(Error $error){echo $error->getMessage();echo "|";}
$result=($object->value="5");echo $result==="5";echo $object->value;
$result=($object->value="peek");echo $result==="peek";
$result=($object->value="2");echo $result==="2";echo $object->value;
$result=($object->value="peek");echo $result==="peek";
'''

CASES = {
    'class-initialized-pure-expression-get-short-set-backing':
        (b'<?php class PlainExpressionPair59 {public int $value=3 '
         b'{get => 700;set => $value+10;}} '
         b'$object=new PlainExpressionPair59;echo $object->value;'
         b'$result=($object->value=5);echo $result;echo $object->value;', b'7005700'),
    'class-absent-pure-expression-get-short-set-uninitialized-and-persistent-backing':
        (PURE_ABSENT_SOURCE, b'700Typed property PureExpressionPair59::$value must not be accessed before initialization|1700K1511700K121'),
    'class-absent-backed-expression-get-short-set-read-error-first-write':
        (b'<?php class BackedExpressionPair59 {public int $value '
         b'{get => $this->value+100;set => $value+10;}} '
         b'$object=new BackedExpressionPair59;try{echo $object->value;}'
         b'catch(Error $error){echo $error->getMessage();echo "|";}'
         b'$result=($object->value=5);echo $result;echo $object->value;'
         b'$result=($object->value=2);echo $result;echo $object->value;',
         b'Typed property BackedExpressionPair59::$value must not be accessed before initialization|51152112'),
    'class-expression-get-short-set-getter-throw-return-type-retry-and-receiver':
        (SOURCE, b'G3;UDC1;1;G15;115;1;G12;112;G12;RT1;G12;112;D5Z'),
    'expression-get-error-before-short-set-variance-error':
        (b'<?php echo "P";class ExpressionPairPriority59 {public int $value=0 '
         b'{get => ($this=1);set(string $supplied) => $supplied;}}echo "Z";', b''),
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
    name = 'expression-get-error-before-short-set-variance-error'
    ticks.STATUSES[name], ticks.EXITS[name] = 'static_rejection', 255
    ticks.main(model_timeout=180)


if __name__ == '__main__':
    main()
