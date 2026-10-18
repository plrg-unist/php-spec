"""Undefined list CV keys retain null conversion despite handler initialization."""

CASES = {
    'list-undefined-key-default-then-null': b'''<?php
function list_undefined_deprecated($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Using null as an array offset is deprecated, use an empty string instead"),":",$l,":",$GLOBALS["key"],":",$GLOBALS["x"],";";
    $GLOBALS["q"]=33;$GLOBALS["key"]=2;$GLOBALS["x"]=99;
    $GLOBALS["a"]=[""=>88,2=>77];$GLOBALS["dest"]=200;
    return true;
}
function list_undefined_first($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "W:",$n,":",($m==='Undefined variable $key'),":",$l,":",$GLOBALS["x"],";";
    $GLOBALS["key"]=1;$GLOBALS["q"]=22;$GLOBALS["x"]=77;
    set_error_handler("list_undefined_deprecated",E_DEPRECATED);
    return false;
}
error_reporting(E_ALL);unset($key);$q=2;$a=[""=>&$q,2=>7];
$x=7;$tail=8;$dest=100;$calls=0;
set_error_handler("list_undefined_first",E_WARNING);
$dest=([
$key=>$x,
$key=>$tail
]=$a);
restore_error_handler();restore_error_handler();
echo "R:",$x,":",$tail,":",$dest[""],":",$dest[2],":",$a[""],":",$a[2],":",$key,":",$calls,";";
unset($a,$dest,$q,$key);
''',
    'list-undefined-key-mixed-warning-expiry': b'''<?php
function list_undefined_expire($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "W:",$n,":",($m==='Undefined variable $key'),":",$l,":",$GLOBALS["x"],";";
    $GLOBALS["q"]=33;$GLOBALS["a"][""]=77;
    $GLOBALS["key"]=2;$GLOBALS["x"]=99;$GLOBALS["outside"]=88;
    set_error_handler("list_undefined_unexpected",E_ALL);
    return true;
}
function list_undefined_unexpected($n,$m,$f,$l) {echo "BAD;";return true;}
unset($key);$q=2;$a=[""=>9,1=>&$q,2=>6];
$outside=8;$y=&$outside;$x=7;$tail=10;$dest=100;$calls=0;
set_error_handler("list_undefined_expire",E_WARNING);
$dest=([
$key=>$x,
1=>&$y,
2=>$tail
]=$a);
restore_error_handler();restore_error_handler();
echo "R:",($x===null),":",$y,":",$outside,":",$tail,":",$dest[""],":",$dest[1],":",$q,":",$calls,";";
$y=55;
echo "A:",$y,":",$q,":",$a[1],":",$dest[1],":",$outside,";";
unset($a,$dest,$q,$y,$key);
echo "U:",isset($a),":",isset($dest),":",isset($q),":",isset($y),";";
''',
    'list-undefined-key-mixed-supplied-throw': b'''<?php
function list_undefined_throw($n,$m,$f,$l) {
    echo "W:",$n,":",($m==='Undefined variable $key'),":",$l,":",$GLOBALS["before"],";";
    $GLOBALS["x"]=99;$GLOBALS["q"]=33;$GLOBALS["key"]=1;$GLOBALS["a"]=null;
    unset($GLOBALS["a"],$GLOBALS["q"],$GLOBALS["key"]);
    throw $GLOBALS["second"];
}
$second=new Exception("kept");unset($key);$q=2;$a=[0=>9,""=>&$q,1=>6];
$before=50;$x=7;$y=8;$dest=100;
set_error_handler("list_undefined_throw",E_ALL);
try {
    $dest=([
    0=>$before,
    $key=>$x,
    1=>&$y
    ]=$a);
} catch (Throwable $e) {
    echo "C:",($e===$second),":",($e->getPrevious()===null),":",$before,":",$x,":",$y,":",$dest,";";
} finally {echo "F;";}
restore_error_handler();
echo "U:",isset($a),":",isset($q),":",isset($key),";";
''',
}

SOURCE_ONLY = {
    'list-undefined-key-deprecated-only-handler': b'''<?php
function list_undefined_only_deprecated($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Using null as an array offset is deprecated, use an empty string instead"),":",$l,":",$GLOBALS["x"],";";
    $GLOBALS["q"]=33;$GLOBALS["key"]=1.5;
    $GLOBALS["a"]=[""=>88,1=>77];
    return true;
}
error_reporting(E_ALL);unset($key);$q=2;$a=[""=>&$q,1=>6];
$x=7;$tail=8;$dest=100;$calls=0;
set_error_handler("list_undefined_only_deprecated",E_DEPRECATED);
$dest=([
$key=>$x,
1=>$tail
]=$a);
restore_error_handler();
echo "R:",$x,":",$tail,":",$dest[""],":",$dest[1],":",$a[""],":",$a[1],":",$key,":",$calls,";";
unset($a,$dest,$q,$key);
''',
}
