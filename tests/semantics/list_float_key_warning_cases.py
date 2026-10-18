"""Lossy list-key conversion before lookup, later keys and throw cancellation."""

CASES = {
    'list-float-key-two-conversions-default': b'''<?php
function list_float_first($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "F:",$n,":",($m==="Implicit conversion from float 2.5 to int loses precision"),":",$l,":",$GLOBALS["x"],";";
    $GLOBALS["key"]=0;$GLOBALS["next"]=-1.5;
    $GLOBALS["a"]=[2=>44,-1=>55];$GLOBALS["x"]=99;$GLOBALS["dest"]=150;
    set_error_handler("list_float_second",E_DEPRECATED);
    return false;
}
function list_float_second($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "S:",$n,":",($m==="Implicit conversion from float -1.5 to int loses precision"),":",$l,":",$GLOBALS["x"],":",$GLOBALS["y"],";";
    $GLOBALS["next"]=false;$GLOBALS["y"]=88;$GLOBALS["dest"]=200;
    return true;
}
error_reporting(E_ALL);$key=2.5;$next=0;$x=7;$y=8;$dest=100;$calls=0;
$a=[2=>22,-1=>11];
set_error_handler("list_float_first",E_DEPRECATED);
$dest=([
$key=>$x,
$next=>$y
]=$a);
restore_error_handler();
echo "R:",$x,":",$y,":",$dest[2],":",$dest[-1],":",$a[2],":",$a[-1],":",$key,":",($next===false),":",$calls,";";
unset($a,$dest);
''',
    'list-float-key-present-null-retire': b'''<?php
function list_float_null($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float 0.5 to int loses precision"),":",$l,":",$GLOBALS["q"],";";
    $GLOBALS["q"]=33;$GLOBALS["next"]=true;$GLOBALS["x"]=99;
    unset($GLOBALS["a"],$GLOBALS["q"],$GLOBALS["key"]);
    return true;
}
$key=0.5;$next=2;$q=2;$a=[0=>null,1=>&$q];
$x=7;$y=8;$dest=100;$calls=0;
set_error_handler("list_float_null");
$dest=([
$key=>$x,
$next=>$y
]=$a);
restore_error_handler();
echo "R:",($x===null),":",$y,":",($dest[0]===null),":",$dest[1],":",isset($a),":",isset($q),":",isset($key),":",$calls,";";
$dest[1]=55;
echo "A:",$y,":",$dest[1],";";
unset($dest);
echo "U:",isset($dest),";";
''',
    'list-float-key-supplied-throw': b'''<?php
function list_float_throw($n,$m,$f,$l) {
    echo "D:",$n,":",($m==="Implicit conversion from float -2.5 to int loses precision"),":",$l,":",$GLOBALS["before"],";";
    $GLOBALS["x"]=99;$GLOBALS["q"]=33;
    unset($GLOBALS["a"],$GLOBALS["q"],$GLOBALS["key"]);
    throw $GLOBALS["second"];
}
$second=new Exception("kept");$key=-2.5;$q=2;$a=[0=>9,-2=>&$q,1=>6];
$before=50;$x=7;$y=8;$dest=100;
set_error_handler("list_float_throw");
try {
    $dest=([
    0=>$before,
    $key=>$x,
    1=>$y
    ]=$a);
} catch (Throwable $e) {
    echo "C:",($e===$second),":",($e->getPrevious()===null),":",$before,":",$x,":",$y,":",$dest,";";
} finally {echo "F;";}
restore_error_handler();
echo "U:",isset($a),":",isset($q),":",isset($key),";";
''',
}

# The source gate also covers default conversion reporting before a handler that
# is eligible only for the subsequent missing-key warning.
SOURCE_ONLY = {
    'list-float-key-warning-only-handler': b'''<?php
function list_float_warning_only($n,$m,$f,$l) {
    echo "W:",$n,":",($m==="Undefined array key 2"),":",$l,":",$GLOBALS["x"],";";
    $GLOBALS["q"]=33;$GLOBALS["x"]=99;$GLOBALS["a"][2]=77;
    return true;
}
error_reporting(E_ALL);$key=2.5;$q=2;$a=[1=>&$q];$x=7;$y=8;
set_error_handler("list_float_warning_only",E_WARNING);
$dest=([
$key=>$x,
1=>$y
]=$a);
restore_error_handler();
echo "R:",($x===null),":",$y,":",$dest[1],":",$a[2],":",isset($dest[2]),";";
unset($a,$dest,$q);
''',
}
