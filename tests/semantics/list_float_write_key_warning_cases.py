"""Writable lossy-key conversion: pre-warning COW, detached NULL and throw."""

CASES = {
    'list-float-write-key-pre-cow-singleton': b'''<?php
function list_float_write_copy($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float 0.5 to int loses precision"),":",$l,":",$GLOBALS["a"][1],":",$GLOBALS["copy"][1],";";
    $GLOBALS["copy"][1]=33;
    $GLOBALS["key"]=3.5;$GLOBALS["next"]=1;$GLOBALS["y"]=99;
    return false;
}
error_reporting(E_ALL);$key=0.5;$next=2;$q=2;
$a=[0=>9,1=>&$q,2=>6];$copy=$a;unset($q);
$y=7;$x=8;$dest=100;$calls=0;
set_error_handler("list_float_write_copy");
$dest=([
$key=>&$y,
$next=>$x
]=$a);
restore_error_handler();
echo "R:",$y,":",$x,":",$a[1],":",$copy[1],":",$a[0],":",$copy[0],":",$dest[0],":",$calls,";";
$y=55;$a[2]=66;
echo "A:",$a[0],":",$dest[0],":",$copy[0],":",$a[2],":",$dest[2],":",$copy[1],";";
unset($a,$copy,$dest,$y);
echo "U:",isset($a),":",isset($copy),":",isset($dest),":",isset($y),";";
''',
    'list-float-write-key-expiry-detaches-target': b'''<?php
function list_float_write_expiry($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float 0.75 to int loses precision"),":",$l,":",$GLOBALS["outside"],";";
    $GLOBALS["q"]=33;$GLOBALS["a"][2]=77;
    $GLOBALS["key"]=false;$GLOBALS["next"]=1;$GLOBALS["outside"]=88;
    return true;
}
$key=0.75;$next=2;$q=2;$a=[0=>9,1=>&$q];
$outside=7;$y=&$outside;$x=8;$dest=100;$calls=0;
set_error_handler("list_float_write_expiry");
$dest=([
$key=>&$y,
$next=>$x
]=$a);
restore_error_handler();
echo "R:",($y===null),":",$outside,":",$x,":",$a[0],":",$dest[0],":",$a[2],":",$calls,";";
$y=55;$q=44;
echo "A:",$y,":",$outside,":",$a[0],":",$dest[0],":",$a[1],":",$dest[1],":",$x,";";
unset($a,$dest,$q,$y,$outside);
echo "U:",isset($a),":",isset($dest),":",isset($q),":",isset($y),";";
''',
    'list-float-write-key-supplied-throw': b'''<?php
function list_float_write_throw($n,$m,$f,$l) {
    echo "D:",$n,":",($m==="Implicit conversion from float 2.5 to int loses precision"),":",$l,":",$GLOBALS["before"],";";
    $GLOBALS["q"]=33;$GLOBALS["y"]=99;$GLOBALS["a"]=null;
    unset($GLOBALS["a"],$GLOBALS["copy"],$GLOBALS["q"],$GLOBALS["key"]);
    throw $GLOBALS["second"];
}
$second=new Exception("kept");$key=2.5;$q=2;$a=[0=>9,2=>&$q,1=>6];$copy=$a;
$before=50;$y=8;$alias=&$y;$later=7;$dest=100;
set_error_handler("list_float_write_throw");
try {
    $dest=([
    0=>$before,
    $key=>&$y,
    1=>$later
    ]=$a);
} catch (Throwable $e) {
    echo "C:",($e===$second),":",($e->getPrevious()===null),":",$before,":",$y,":",$alias,":",$later,":",$dest,";";
} finally {echo "F;";}
restore_error_handler();
echo "U:",isset($a),":",isset($copy),":",isset($q),":",isset($key),";";
''',
}
