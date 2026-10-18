"""Undefined list keys keep historical tables through two conversion callbacks."""

CASES = {
    'list-undefined-key-review-detached-survivor': b'''<?php
function list_undefined_peer_deprecated($n,$m,$f,$l) {
    echo "D:",$n,":",($m==="Using null as an array offset is deprecated, use an empty string instead"),":",$l,";";
    $GLOBALS["oldq"]=55;$GLOBALS["key"]=2.5;$GLOBALS["next"]=1;
    $GLOBALS["x"]=99;$GLOBALS["dest"]=200;
    return true;
}
function list_undefined_peer_initial($n,$m,$f,$l) {
    echo "U:",$n,":",($m==='Undefined variable $key'),":",$l,";";
    $GLOBALS["hold"]=$GLOBALS["a"];
    $GLOBALS["a"]=[""=>22,1=>44];
    unset($GLOBALS["a"]);$GLOBALS["a"]=&$GLOBALS["replacement"];
    $GLOBALS["q"]=33;unset($GLOBALS["q"]);$GLOBALS["q"]=&$GLOBALS["q_replacement"];
    $GLOBALS["key"]=&$GLOBALS["key_replacement"];$GLOBALS["next"]=0;
    $GLOBALS["x"]=77;$GLOBALS["dest"]=150;
    set_error_handler("list_undefined_peer_deprecated",E_ALL);
    return true;
}
error_reporting(0);$q=2;$oldq=&$q;$q_replacement=66;$key_replacement=1;$next=0;
$a=[""=>&$q,1=>6];$replacement=[""=>88,1=>77];$hold=null;$x=7;$y=8;$dest=100;
unset($key);set_error_handler("list_undefined_peer_initial",E_ALL);
$dest=([
$key=>$x,
$next=>&$y
]=$a);
restore_error_handler();restore_error_handler();
echo "R:",$x,":",$y,":",$dest[""],":",$dest[1],":",$a[""],":",$a[1],":",$hold[""],":",$hold[1],":",$q,":",$oldq,":",$key,";";
$y=85;$oldq=65;$q=70;
echo "A:",$x,":",$hold[""],":",$dest[1],":",$a[1],":",$q,":",$q_replacement,";";
unset($a,$replacement,$hold,$dest,$q,$oldq,$q_replacement,$key,$key_replacement,$next,$x,$y);
echo "U:",isset($a),":",isset($hold),":",isset($key),";";
''',
    'list-undefined-key-review-three-handlers': b'''<?php
function list_undefined_peer_missing($n,$m,$f,$l) {
    echo "W:",$n,":",($m==='Undefined array key ""'),":",$l,":",$GLOBALS["x"],":",$GLOBALS["before"],";";
    $GLOBALS["a"][""]=66;$GLOBALS["q"]=55;$GLOBALS["next"]=1;
    $GLOBALS["x"]=99;$GLOBALS["dest"]=200;
    return false;
}
function list_undefined_peer_middle($n,$m,$f,$l) {
    echo "D:",$n,":",($m==="Using null as an array offset is deprecated, use an empty string instead"),":",$l,":",$GLOBALS["x"],":",$GLOBALS["before"],";";
    $GLOBALS["key"]=2.5;$GLOBALS["next"]=2.5;$GLOBALS["q"]=44;$GLOBALS["x"]=88;
    set_error_handler("list_undefined_peer_missing",E_ALL);
    return true;
}
function list_undefined_peer_first($n,$m,$f,$l) {
    echo "U:",$n,":",($m==='Undefined variable $key'),":",$l,":",$GLOBALS["before"],";";
    $GLOBALS["key"]=9.5;$GLOBALS["next"]=9.5;$GLOBALS["q"]=33;
    $GLOBALS["x"]=77;$GLOBALS["dest"]=150;
    set_error_handler("list_undefined_peer_middle",E_ALL);
    return true;
}
error_reporting(0);$q=2;$a=[0=>9,1=>&$q];$copy=$a;$next=0;
$before=50;$x=7;$y=8;$dest=100;unset($key);
set_error_handler("list_undefined_peer_first",E_ALL);
$dest=([
0=>$before,
$key=>$x,
$next=>&$y
]=$a);
restore_error_handler();restore_error_handler();restore_error_handler();
echo "R:",$before,":",($x===null),":",$y,":",$dest[""],":",$dest[1],":",isset($copy[""]),":",$copy[1],":",$a[""],":",$key,":",$next,";";
$y=77;
echo "A:",$q,":",$copy[1],":",$dest[1],":",$a[1],":",($x===null),";";
unset($a,$copy,$dest,$q,$before,$x,$y,$key,$next);
echo "U:",isset($a),":",isset($copy),":",isset($dest),";";
''',
}
