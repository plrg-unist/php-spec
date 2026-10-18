"""Surviving protected tables and detached mixed-list source cells."""

CASES = {
    'list-float-ref-review-cow-copy-survives': b'''<?php
function list_float_ref_peer($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float 2.5 to int loses precision"),":",$l,":",$GLOBALS["early"],";";
    $GLOBALS["hold"]=$GLOBALS["a"];$GLOBALS["q"]=33;
    $GLOBALS["a"]=[0=>90,2=>22,1=>44];$GLOBALS["key"]=false;
    $GLOBALS["x"]=99;$GLOBALS["dest"]=200;
    return false;
}
error_reporting(0);$key=2.5;$q=2;$a=[0=>9,2=>&$q,1=>6];$copy=$a;
$early=50;$x=7;$y=8;$dest=100;$hold=null;$calls=0;
set_error_handler("list_float_ref_peer",E_DEPRECATED);
$dest=([
0=>&$early,
$key=>$x,
1=>&$y
]=$a);
restore_error_handler();
echo "R:",$x,":",$y,":",$early,":",$dest[2],":",$a[2],":",$hold[2],":",$copy[2],":",$calls,";";
$early=55;$y=66;
echo "A:",$hold[0],":",$copy[0],":",$a[0],":",$a[1],":",$dest[1],":",$hold[1],":",$copy[1],":",$q,";";
unset($a,$dest,$hold,$copy,$q,$early,$y);
echo "U:",isset($a),":",isset($dest),":",isset($hold),";";
''',
    'list-float-ref-review-detached-missing-cell': b'''<?php
function list_float_ref_peer_second($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "W:",$n,":",($m==="Undefined array key -2"),":",$l,":",$GLOBALS["x"],";";
    $GLOBALS["q_alias"]=55;$GLOBALS["next"]=1;
    $GLOBALS["x"]=99;$GLOBALS["a"][-2]=77;
    return true;
}
function list_float_ref_peer_first($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float -2.75 to int loses precision"),":",$l,":",$GLOBALS["x"],";";
    $GLOBALS["key_alias"]=17.5;
    unset($GLOBALS["key"],$GLOBALS["key_alias"],$GLOBALS["a"]);
    $GLOBALS["key"]=&$GLOBALS["key_replacement"];
    $GLOBALS["a"]=&$GLOBALS["replacement"];
    $GLOBALS["q"]=33;unset($GLOBALS["q"]);
    $GLOBALS["q"]=&$GLOBALS["other"];$GLOBALS["q"]=44;
    $GLOBALS["next"]=0.5;$GLOBALS["x"]=77;$GLOBALS["dest"]=200;
    set_error_handler("list_float_ref_peer_second",E_WARNING);
    return true;
}
error_reporting(0);$key=-2.75;$key_alias=&$key;$key_replacement=9.5;$next=0;
$q=2;$q_alias=&$q;$other=8;$a=[0=>6,1=>&$q];$replacement=[0=>88,1=>44];
$x=7;$y=8;$dest=100;$calls=0;
set_error_handler("list_float_ref_peer_first",E_DEPRECATED);
$dest=([
$key=>$x,
$next=>&$y
]=$a);
restore_error_handler();
echo "R:",($x===null),":",$y,":",$dest[1],":",$a[1],":",$q,":",$other,":",$key,":",$key_replacement,":",$a[-2],":",isset($dest[-2]),":",$calls,";";
$y=66;$key=12.5;
echo "A:",$dest[1],":",$q_alias,":",$a[1],":",$q,":",$key,":",$key_replacement,";";
unset($dest,$a,$replacement,$q,$q_alias,$other,$y,$key,$key_replacement);
echo "U:",isset($dest),":",isset($a),":",isset($key_alias),";";
''',
}
