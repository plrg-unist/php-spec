"""NULL list reference keys freeze empty selection across deprecation callbacks."""

CASES = {
    'list-null-write-key-null-unique': b'''<?php
function list_null_write_unique($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Using null as an array offset is deprecated, use an empty string instead"),":",$l,":",($GLOBALS["a"]===[]),":",($GLOBALS["alias"]===[]),";";
    $GLOBALS["outside"]=88;$GLOBALS["key"]=1.5;$GLOBALS["next"]=1;
    return false;
}
error_reporting(E_ALL);$key=null;$next=0;$a=null;$alias=&$a;
$outside=8;$x=&$outside;$y=9;$dest=100;$calls=0;
set_error_handler("list_null_write_unique",E_DEPRECATED);
$dest=([
$key=>&$x,
$next=>&$y
]=$a);
restore_error_handler();
echo "R:",($x===null),":",($y===null),":",$outside,":",($a===[""=>null,1=>null]),":",($alias===[""=>null,1=>null]),":",($dest===[""=>null,1=>null]),":",$key,":",$calls,";";
$x=55;$y=77;
echo "A:",$a[""],":",$alias[""],":",$dest[""],":",$a[1],":",$alias[1],":",$dest[1],":",$outside,";";
unset($a,$alias,$dest,$x,$y,$key,$next);
echo "U:",isset($a),":",isset($alias),":",isset($x),";";
''',
    'list-null-write-key-false-expiry': b'''<?php
function list_null_write_expire($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Using null as an array offset is deprecated, use an empty string instead"),":",$l,":",($GLOBALS["a"]===[]),";";
    $GLOBALS["a"][""]=77;$GLOBALS["a"][1]=&$GLOBALS["q"];
    $GLOBALS["q"]=33;$GLOBALS["outside"]=88;$GLOBALS["key"]=0.75;$GLOBALS["next"]=1;
    set_error_handler("list_null_write_unexpected",E_ALL);
    return true;
}
function list_null_write_unexpected($n,$m,$f,$l) {echo "BAD;";return true;}
error_reporting(0);$key=null;$next=0;$q=2;$a=false;
$outside=8;$x=&$outside;$y=7;$dest=100;$calls=0;
set_error_handler("list_null_write_expire",E_ALL);
$dest=([
$key=>&$x,
$next=>$y
]=$a);
restore_error_handler();restore_error_handler();
echo "R:",($x===null),":",$y,":",$outside,":",$a[""],":",$dest[""],":",$dest[1],":",$key,":",$calls,";";
$x=55;$q=44;
echo "A:",$x,":",$a[""],":",$dest[""],":",$y,":",$a[1],":",$dest[1],":",$outside,";";
unset($a,$dest,$q,$x,$key,$next);
echo "U:",isset($a),":",isset($dest),":",isset($q),";";
''',
    'list-null-write-key-supplied-throw': b'''<?php
function list_null_write_throw($n,$m,$f,$l) {
    echo "D:",$n,":",($m==="Using null as an array offset is deprecated, use an empty string instead"),":",$l,":",$GLOBALS["before"],";";
    $GLOBALS["outside"]=99;$GLOBALS["q"]=33;$GLOBALS["key"]=1.5;$GLOBALS["a"]=null;
    unset($GLOBALS["a"],$GLOBALS["q"],$GLOBALS["key"]);
    throw $GLOBALS["second"];
}
$second=new Exception("kept");$key=null;$q=2;$a=[0=>9,""=>&$q,1=>6];
$outside=8;$x=&$outside;$before=50;$y=7;$dest=100;
set_error_handler("list_null_write_throw",E_ALL);
try {
    $dest=([
    0=>$before,
    $key=>&$x,
    1=>$y
    ]=$a);
} catch (Throwable $e) {
    echo "C:",($e===$second),":",($e->getPrevious()===null),":",$before,":",$x,":",$outside,":",$y,":",$dest,";";
} finally {echo "F;";}
restore_error_handler();
echo "U:",isset($a),":",isset($q),":",isset($key),";";
''',
}
