"""NULL CV list keys: conversion, missing lookup, protection and cancellation."""

CASES = {
    'list-null-key-default-missing-order': b'''<?php
function list_null_first($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Using null as an array offset is deprecated, use an empty string instead"),":",$l,":",$GLOBALS["x"],";";
    $GLOBALS["key"]=1.5;$GLOBALS["next"]=null;$GLOBALS["q"]=33;
    $GLOBALS["a"][""]=77;$GLOBALS["x"]=77;$GLOBALS["dest"]=150;
    set_error_handler("list_null_missing",E_WARNING);
    return false;
}
function list_null_missing($n,$m,$f,$l) {
    $GLOBALS["calls"]++;$GLOBALS["warnings"]++;
    echo "W:",$n,":",($m==='Undefined array key ""'),":",$l,":",$GLOBALS["x"],":",$GLOBALS["y"],";";
    if ($GLOBALS["warnings"]===1) {
        $GLOBALS["x"]=88;$GLOBALS["y"]=66;$GLOBALS["next"]=null;
    } else {
        $GLOBALS["x"]=99;$GLOBALS["y"]=55;$GLOBALS["next"]=false;
    }
    $GLOBALS["dest"]=200;
    return true;
}
error_reporting(E_ALL);$key=null;$next=1;$q=2;$a=[1=>&$q,"present"=>null];
$x=7;$y=8;$z=9;$tail=10;$dest=100;$calls=0;$warnings=0;
set_error_handler("list_null_first",E_DEPRECATED);
$dest=([
$key=>$x,
$next=>$y,
"present"=>$z,
1=>$tail
]=$a);
restore_error_handler();
echo "R:",$x,":",($y===null),":",($z===null),":",$tail,":",$dest[1],":",$a[""],":",isset($dest[""]),":",$key,":",($next===false),":",$calls,":",$warnings,";";
unset($a,$dest,$q,$key,$next);
''',
    'list-null-key-mixed-protection-expiry': b'''<?php
function list_null_expire($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Using null as an array offset is deprecated, use an empty string instead"),":",$l,":",$GLOBALS["x"],";";
    $GLOBALS["q"]=33;$GLOBALS["a"][""]=77;
    $GLOBALS["key"]=false;$GLOBALS["x"]=99;$GLOBALS["outside"]=88;
    set_error_handler("list_null_unexpected",E_WARNING);
    return true;
}
function list_null_unexpected($n,$m,$f,$l) {echo "BAD;";return true;}
$key=null;$q=2;$a=[""=>9,1=>&$q,2=>6];
$outside=8;$y=&$outside;$x=7;$tail=10;$dest=100;$calls=0;
set_error_handler("list_null_expire",E_DEPRECATED);
$dest=([
$key=>$x,
1=>&$y,
2=>$tail
]=$a);
restore_error_handler();
echo "R:",($x===null),":",$y,":",$outside,":",$tail,":",$dest[""],":",$dest[1],":",$q,":",$calls,";";
$y=55;
echo "A:",$y,":",$q,":",$a[1],":",$dest[1],":",$outside,";";
unset($a,$dest,$q,$y);
echo "U:",isset($a),":",isset($dest),":",isset($q),":",isset($y),";";
''',
    'list-null-key-mixed-supplied-throw': b'''<?php
function list_null_throw($n,$m,$f,$l) {
    echo "D:",$n,":",($m==="Using null as an array offset is deprecated, use an empty string instead"),":",$l,":",$GLOBALS["before"],";";
    $GLOBALS["x"]=99;$GLOBALS["q"]=33;$GLOBALS["a"]=null;
    unset($GLOBALS["a"],$GLOBALS["q"],$GLOBALS["key"]);
    throw $GLOBALS["second"];
}
$second=new Exception("kept");$key=null;$q=2;$a=[0=>9,""=>&$q,1=>6];
$before=50;$x=7;$y=8;$dest=100;
set_error_handler("list_null_throw",E_DEPRECATED);
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
