"""NULL-key conversion freezes empty bytes before source/key name rebinding."""

CASES = {
    'list-null-key-review-present-retired-cells': b'''<?php
function list_null_key_peer_present($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Using null as an array offset is deprecated, use an empty string instead"),":",$l,";";
    $GLOBALS["q"]=33;
    unset($GLOBALS["a"],$GLOBALS["q"],$GLOBALS["key"],$GLOBALS["key_alias"]);
    $GLOBALS["a"]=&$GLOBALS["replacement"];
    $GLOBALS["q"]=&$GLOBALS["q_replacement"];
    $GLOBALS["key"]=&$GLOBALS["key_replacement"];
    $GLOBALS["x"]=99;$GLOBALS["tail"]=88;$GLOBALS["dest"]=200;
    return true;
}
error_reporting(0);$q=2;$key=null;$key_alias=&$key;$key_replacement=1;$q_replacement=66;
$a=[""=>&$q,1=>6];$replacement=[""=>88,1=>77];$x=7;$tail=8;$dest=100;$calls=0;
set_error_handler("list_null_key_peer_present",E_ALL);
$dest=([
$key=>$x,
$key=>$tail
]=$a);
restore_error_handler();
echo "R:",$x,":",$tail,":",$dest[""],":",$dest[1],":",$a[""],":",$a[1],":",$q,":",$key,":",isset($key_alias),":",$calls,";";
$dest[""]=55;$q=77;$x=70;
echo "A:",$x,":",$dest[""],":",$a[""],":",$q,":",$q_replacement,";";
unset($a,$replacement,$dest,$q,$q_replacement,$x,$tail,$key,$key_replacement);
echo "U:",isset($a),":",isset($dest),":",isset($key_alias),";";
''',
    'list-null-key-review-missing-replacement-handler': b'''<?php
function list_null_key_peer_warning($n,$m,$f,$l) {
    $GLOBALS["warning_calls"]++;
    echo "W:",$n,":",($m==='Undefined array key ""'),":",$l,":",$GLOBALS["x"],":",$GLOBALS["before"],";";
    $GLOBALS["hold"][""]=66;$GLOBALS["q"]=55;$GLOBALS["next"]=1;$GLOBALS["x"]=99;
    return false;
}
function list_null_key_peer_deprecated($n,$m,$f,$l) {
    $GLOBALS["deprecated_calls"]++;
    echo "D:",$n,":",($m==="Using null as an array offset is deprecated, use an empty string instead"),":",$l,";";
    $GLOBALS["hold"]=&$GLOBALS["a"];
    unset($GLOBALS["a"]);$GLOBALS["a"]=&$GLOBALS["replacement"];
    $GLOBALS["q"]=33;$GLOBALS["key"]=2.5;$GLOBALS["next"]=2.5;$GLOBALS["x"]=77;$GLOBALS["dest"]=200;
    set_error_handler("list_null_key_peer_warning",E_ALL);
    return true;
}
error_reporting(0);$q=2;$a=[0=>9,1=>&$q];$replacement=[""=>88,1=>44];$key=null;$next=0;
$before=50;$x=7;$y=8;$dest=100;$hold=null;$deprecated_calls=0;$warning_calls=0;
set_error_handler("list_null_key_peer_deprecated",E_ALL);
$dest=([
0=>$before,
$key=>$x,
$next=>&$y
]=$a);
restore_error_handler();restore_error_handler();
echo "R:",$before,":",($x===null),":",$y,":",$dest[""],":",$dest[1],":",$a[""],":",$a[1],":",$hold[""],":",$deprecated_calls,":",$warning_calls,";";
$y=77;
echo "A:",$q,":",$hold[1],":",$dest[1],":",$a[1],":",($x===null),";";
unset($a,$replacement,$hold,$dest,$q,$x,$y,$key,$next);
echo "U:",isset($a),":",isset($dest),":",isset($hold),";";
''',
}
