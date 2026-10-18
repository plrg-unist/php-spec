"""NULL writable keys: pre-COW sole hold and live shared cancellation."""

CASES = {
    'list-null-write-review-detached-sole-hold': b'''<?php
function list_null_write_peer_hold($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Using null as an array offset is deprecated, use an empty string instead"),":",$l,";";
    $GLOBALS["hold"]=$GLOBALS["a"];$GLOBALS["q"]=33;
    $GLOBALS["a"]=[1=>22,2=>44];
    unset($GLOBALS["a"],$GLOBALS["key"],$GLOBALS["key_alias"]);
    $GLOBALS["a"]=&$GLOBALS["replacement"];
    $GLOBALS["key"]=&$GLOBALS["key_replacement"];
    $GLOBALS["x"]=99;$GLOBALS["tail"]=88;$GLOBALS["dest"]=200;
    return true;
}
error_reporting(0);$key=null;$key_alias=&$key;$key_replacement=1;
$q=2;$a=[0=>6,1=>&$q];$copy=$a;$replacement=[1=>88,2=>66];
$x=7;$outside=&$x;$tail=8;$dest=100;$hold=null;$calls=0;
set_error_handler("list_null_write_peer_hold",E_ALL);
$dest=([
$key=>&$x,
$key=>&$tail
]=$a);
restore_error_handler();
echo "R:",($x===null),":",$tail,":",$outside,":",$dest[1],":",$dest[2],":",$a[1],":",$a[2],":",($hold[""]===null),":",isset($copy[""]),":",$hold[1],":",$copy[1],":",$key,":",$calls,";";
$x=55;$tail=77;$key=2;
echo "A:",$hold[""],":",$dest[1],":",$a[1],":",isset($copy[""]),":",$q,":",$key_replacement,":",$outside,";";
unset($a,$replacement,$dest,$hold,$copy,$q,$x,$outside,$tail,$key,$key_replacement);
echo "U:",isset($a),":",isset($dest),":",isset($key_alias),";";
''',
    'list-null-write-review-live-shared-cancel': b'''<?php
function list_null_write_peer_shared($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Using null as an array offset is deprecated, use an empty string instead"),":",$l,":",$GLOBALS["before"],";";
    $GLOBALS["hold"]=$GLOBALS["a"];$GLOBALS["q"]=33;
    $GLOBALS["key"]=7;$GLOBALS["next"]=2;
    $GLOBALS["x"]=99;$GLOBALS["dest"]=200;
    return false;
}
error_reporting(0);$key=null;$next=0;$q=2;$a=[0=>9,""=>&$q,2=>6];
$x=7;$outside=&$x;$before=50;$tail=8;$dest=100;$hold=null;$calls=0;
set_error_handler("list_null_write_peer_shared",E_ALL);
$dest=([
0=>$before,
$key=>&$x,
$next=>$tail
]=$a);
restore_error_handler();
echo "R:",($x===null),":",$outside,":",$q,":",$a[""],":",$hold[""],":",$dest[""],":",$tail,":",$before,":",$calls,";";
$x=55;$q=44;
echo "A:",$x,":",$outside,":",$q,":",$a[""],":",$hold[""],":",$dest[""],";";
unset($a,$dest,$hold,$q,$x,$outside,$key,$next);
echo "U:",isset($a),":",isset($dest),":",isset($hold),";";
''',
}
