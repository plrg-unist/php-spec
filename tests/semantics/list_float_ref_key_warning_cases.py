"""Mixed list-key conversion protection, source-cell authority and expiry."""

CASES = {
    'list-float-ref-key-insert-expiry': b'''<?php
function list_float_ref_unexpected($n,$m,$f,$l) {
    echo "BAD:",$n,":",$l,";";
    return true;
}
function list_float_ref_insert($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float 0.5 to int loses precision"),":",$l,":",$GLOBALS["q"],";";
    $GLOBALS["q"]=33;$GLOBALS["a"][0]=77;
    $GLOBALS["key"]=3.5;$GLOBALS["next"]=1;
    $GLOBALS["x"]=99;$GLOBALS["y"]=88;
    set_error_handler("list_float_ref_unexpected");
    return false;
}
error_reporting(E_ALL);$key=0.5;$next=2;$q=2;$a=[1=>&$q,2=>6];
$x=7;$y=8;$dest=100;$calls=0;
set_error_handler("list_float_ref_insert");
$dest=([
$key=>$x,
$next=>&$y
]=$a);
restore_error_handler();
echo "R:",($x===null),":",$y,":",$q,":",$a[0],":",$dest[0],":",$calls,";";
$y=55;$a[0]=88;
echo "A:",$y,":",$q,":",$a[1],":",$dest[1],":",$a[0],":",$dest[0],";";
unset($a,$dest,$q,$y);
echo "U:",isset($a),":",isset($dest),":",isset($q),":",isset($y),";";
''',
    'list-float-ref-key-null-rebind': b'''<?php
function list_float_ref_null($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float 0.5 to int loses precision"),":",$l,":",$GLOBALS["q"],";";
    $GLOBALS["q"]=33;$GLOBALS["a"]=null;$GLOBALS["x"]=99;
    unset($GLOBALS["a"],$GLOBALS["q"],$GLOBALS["key"]);
    $GLOBALS["a"]=&$GLOBALS["other"];
    $GLOBALS["key"]=&$GLOBALS["replacement"];
    return true;
}
$key=0.5;$replacement=2.5;$q=2;$a=[0=>9,1=>&$q];$other=[1=>44];
$x=7;$y=8;$dest=100;$calls=0;
set_error_handler("list_float_ref_null");
$dest=([
$key=>$x,
1=>&$y
]=$a);
restore_error_handler();
echo "R:",($x===null),":",($y===null),":",($dest[1]===null),":",$a[1],":",$other[1],":",$key,":",$replacement,":",isset($q),":",$calls,";";
$y=55;
echo "A:",$y,":",$dest[1],":",$a[1],":",isset($dest[0]),";";
unset($dest,$y,$a,$other,$key,$replacement);
echo "U:",isset($dest),":",isset($y),":",isset($a),";";
''',
    'list-float-ref-key-supplied-throw': b'''<?php
function list_float_ref_throw($n,$m,$f,$l) {
    echo "D:",$n,":",($m==="Implicit conversion from float -2.5 to int loses precision"),":",$l,":",$GLOBALS["before"],";";
    $GLOBALS["x"]=99;$GLOBALS["q"]=33;$GLOBALS["a"]=null;
    unset($GLOBALS["a"],$GLOBALS["q"],$GLOBALS["key"]);
    throw $GLOBALS["second"];
}
$second=new Exception("kept");$key=-2.5;$q=2;$a=[0=>9,-2=>&$q,1=>6];
$before=50;$x=7;$y=8;$dest=100;
set_error_handler("list_float_ref_throw");
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
