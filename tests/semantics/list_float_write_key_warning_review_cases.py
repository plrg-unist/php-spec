"""Writable-key conversion: detached sole hold versus a live shared table."""

CASES = {
    'list-float-write-review-detached-sole-hold': b'''<?php
function list_float_write_peer_unique($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float -2.75 to int loses precision"),":",$l,";";
    $GLOBALS["hold"]=$GLOBALS["a"];$GLOBALS["q"]=33;
    $GLOBALS["a"]=[-2=>22,1=>44];
    unset($GLOBALS["a"],$GLOBALS["key"],$GLOBALS["key_alias"]);
    $GLOBALS["a"]=&$GLOBALS["replacement"];
    $GLOBALS["key"]=&$GLOBALS["key_replacement"];
    $GLOBALS["x"]=99;$GLOBALS["tail"]=88;$GLOBALS["dest"]=200;
    return true;
}
error_reporting(0);$key=-2.75;$key_alias=&$key;$key_replacement=9.5;
$q=2;$a=[0=>6,1=>&$q];$copy=$a;$replacement=[-2=>88,1=>66];
$x=7;$tail=8;$dest=100;$hold=null;$calls=0;
set_error_handler("list_float_write_peer_unique",E_DEPRECATED);
$dest=([
$key=>&$x,
1=>$tail
]=$a);
restore_error_handler();
echo "R:",($x===null),":",$tail,":",$dest[-2],":",$dest[1],":",$a[-2],":",$a[1],":",($hold[-2]===null),":",isset($copy[-2]),":",$hold[1],":",$copy[1],":",$key,":",$calls,";";
$x=55;$key=12.5;
echo "A:",$hold[-2],":",$dest[-2],":",$a[-2],":",isset($copy[-2]),":",$q,":",$key_replacement,";";
unset($a,$replacement,$dest,$hold,$copy,$q,$x,$key,$key_replacement);
echo "U:",isset($a),":",isset($dest),":",isset($key_alias),";";
''',
    'list-float-write-review-live-shared-cancel': b'''<?php
function list_float_write_peer_shared($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float 1.5 to int loses precision"),":",$l,":",$GLOBALS["before"],";";
    $GLOBALS["hold"]=$GLOBALS["a"];$GLOBALS["q"]=33;
    $GLOBALS["key"]=-2.5;$GLOBALS["next"]=2;
    $GLOBALS["x"]=99;$GLOBALS["dest"]=200;
    return false;
}
error_reporting(0);$key=1.5;$next=0;$q=2;$a=[0=>9,1=>&$q,2=>6];
$x=7;$outside=&$x;$before=50;$tail=8;$dest=100;$hold=null;$calls=0;
set_error_handler("list_float_write_peer_shared",E_DEPRECATED);
$dest=([
0=>$before,
$key=>&$x,
$next=>$tail
]=$a);
restore_error_handler();
echo "R:",($x===null),":",$outside,":",$q,":",$a[1],":",$hold[1],":",$dest[1],":",$tail,":",$before,":",$calls,";";
$x=55;
echo "A:",$x,":",$outside,":",$q,":",$a[1],":",$hold[1],":",$dest[1],";";
unset($a,$dest,$hold,$q,$x,$outside);
echo "U:",isset($a),":",isset($dest),":",isset($hold),";";
''',
}
