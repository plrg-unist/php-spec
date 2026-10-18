"""Autovivified writable tables: detached sole hold and live shared cancellation."""

CASES = {
    'list-float-autovivify-review-null-detached-hold': b'''<?php
function list_float_autovivify_peer_hold($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float -2.75 to int loses precision"),":",$l,":",($GLOBALS["a"]===[]),";";
    $GLOBALS["hold"]=$GLOBALS["a"];
    $GLOBALS["a"]=[-2=>22,1=>44];
    unset($GLOBALS["a"],$GLOBALS["key"],$GLOBALS["key_alias"]);
    $GLOBALS["a"]=&$GLOBALS["replacement"];
    $GLOBALS["key"]=&$GLOBALS["key_replacement"];
    $GLOBALS["x"]=99;$GLOBALS["tail"]=88;$GLOBALS["dest"]=200;
    return true;
}
error_reporting(0);$a=null;$key=-2.75;$key_alias=&$key;$key_replacement=9.5;
$replacement=[-2=>88,1=>66];$x=7;$tail=8;$dest=100;$hold=null;$calls=0;
set_error_handler("list_float_autovivify_peer_hold",E_ALL);
$dest=([
$key=>&$x,
1=>&$tail
]=$a);
restore_error_handler();
echo "R:",($x===null),":",$tail,":",$dest[-2],":",$dest[1],":",$a[-2],":",$a[1],":",($hold===[-2=>null]),":",($hold[-2]===null),":",isset($hold[1]),":",$key,":",$calls,";";
$x=55;$tail=77;$key=12.5;
echo "A:",$hold[-2],":",$dest[-2],":",$dest[1],":",$a[1],":",$key_replacement,";";
unset($a,$replacement,$dest,$hold,$x,$tail,$key,$key_replacement);
echo "U:",isset($a),":",isset($dest),":",isset($key_alias),";";
''',
    'list-float-autovivify-review-false-shared-cancel': b'''<?php
function list_float_autovivify_peer_shared($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float 0.75 to int loses precision"),":",$l,":",($GLOBALS["a"]===[]),";";
    $GLOBALS["hold"]=$GLOBALS["a"];
    $GLOBALS["key"]=2.5;$GLOBALS["next"]=1;
    $GLOBALS["x"]=99;$GLOBALS["dest"]=200;
    return false;
}
error_reporting(0);$a=false;$key=0.75;$next=0;
$x=7;$outside=&$x;$tail=8;$dest=100;$hold=null;$calls=0;
set_error_handler("list_float_autovivify_peer_shared",E_ALL);
$dest=([
$key=>&$x,
$next=>&$tail
]=$a);
restore_error_handler();
echo "R:",($x===null),":",($tail===null),":",$outside,":",($a===[1=>null]),":",($hold===[]),":",($dest===[1=>null]),":",isset($a[0]),":",($a===$dest),":",isset($hold[1]),":",$calls,";";
$x=55;$tail=77;
echo "A:",$x,":",$outside,":",$a[1],":",$dest[1],":",($hold===[]),":",isset($a[0]),";";
unset($a,$dest,$hold,$x,$outside,$tail,$key,$next);
echo "U:",isset($a),":",isset($dest),":",isset($hold),";";
''',
}
