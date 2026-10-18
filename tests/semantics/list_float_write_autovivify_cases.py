"""Writable source initialization precedes the lossy-key callback."""

CASES = {
    'list-float-write-autovivify-null-unique': b'''<?php
function list_float_write_null($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float 0.5 to int loses precision"),":",$l,":",($GLOBALS["a"]===[]),":",($GLOBALS["source"]===[]),";";
    $GLOBALS["key"]=9.5;$GLOBALS["next"]=0;$GLOBALS["y"]=99;
    return false;
}
error_reporting(E_ALL);$a=null;$source=&$a;$key=0.5;$next=1;
$y=7;$x=8;$dest=100;$calls=0;
set_error_handler("list_float_write_null");
$dest=([
$key=>&$y,
$next=>$x
]=$a);
restore_error_handler();
echo "R:",($y===null),":",($x===null),":",($a[0]===null),":",($dest[0]===null),":",$calls,";";
$y=55;
echo "A:",$a[0],":",$source[0],":",$dest[0],":",($x===null),";";
unset($a,$source,$dest,$y);
echo "U:",isset($a),":",isset($source),":",isset($dest),":",isset($y),";";
''',
    'list-float-write-autovivify-false-expiry': b'''<?php
function list_float_write_false($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float 0.75 to int loses precision"),":",$l,":",($GLOBALS["a"]===[]),":",$GLOBALS["outside"],";";
    $GLOBALS["a"][1]=33;$GLOBALS["key"]=false;$GLOBALS["next"]=1;$GLOBALS["outside"]=88;
    return true;
}
error_reporting(E_ALL);$a=false;$key=0.75;$next=2;
$outside=7;$y=&$outside;$x=8;$dest=100;$calls=0;
set_error_handler("list_float_write_false");
$dest=([
$key=>&$y,
$next=>$x
]=$a);
restore_error_handler();
echo "R:",($y===null),":",$outside,":",$x,":",$a[1],":",$dest[1],":",isset($a[0]),":",$calls,";";
$y=55;$a[1]=44;
echo "A:",$y,":",$outside,":",$a[1],":",$dest[1],":",$x,";";
unset($a,$dest,$y,$outside);
echo "U:",isset($a),":",isset($dest),":",isset($y),":",isset($outside),";";
''',
    'list-float-write-autovivify-undefined-throw': b'''<?php
function list_float_write_undefined($n,$m,$f,$l) {
    echo "D:",$n,":",($m==="Implicit conversion from float -2.75 to int loses precision"),":",$l,":",($GLOBALS["a"]===[]),":",($GLOBALS["before"]===null),";";
    $GLOBALS["y"]=99;$GLOBALS["a"]=null;
    unset($GLOBALS["a"],$GLOBALS["key"]);
    throw $GLOBALS["second"];
}
error_reporting(E_ALL);$second=new Exception("kept");$key=-2.75;unset($a);
$before=50;$y=8;$alias=&$y;$later=7;$dest=100;
set_error_handler("list_float_write_undefined");
try {
    $dest=([
    0=>$before,
    $key=>&$y,
    1=>$later
    ]=$a);
} catch (Throwable $e) {
    echo "C:",($e===$second),":",($e->getPrevious()===null),":",($before===null),":",$y,":",$alias,":",$later,":",$dest,";";
} finally {echo "F;";}
restore_error_handler();
echo "U:",isset($a),":",isset($key),";";
''',
}
