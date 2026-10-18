"""Pooled NULL descent and runtime literal child/result authority."""

CASES = {
    'list-literal-cv-review-pooled-null-key-retire': b'''<?php
function list_literal_cv_peer($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "H:",$n,":",($m==="Undefined array key 0"),":",$l,";";
    $GLOBALS["outer_alias"]=9;
    unset($GLOBALS["outer"],$GLOBALS["outer_alias"]);
    $GLOBALS["outer"]=&$GLOBALS["replacement"];
    $GLOBALS["middle"]=2.5;$GLOBALS["tailkey"]=true;
    $GLOBALS["x"]=99;$GLOBALS["y"]=88;
    return false;
}
error_reporting(0);$outer=false;$outer_alias=&$outer;$replacement=7;$middle=0;$tailkey=false;
$x=7;$y=8;$tail=9;$calls=0;
set_error_handler("list_literal_cv_peer",E_WARNING);
[
$outer=>[
$middle=>[
[$x,$y]
]
],
$tailkey=>$tail
]=[1=>3];
restore_error_handler();
echo "R:",($x===null),":",($y===null),":",$tail,":",$outer,":",$replacement,":",$middle,":",isset($outer_alias),":",$calls,";";
$outer=9;
echo "A:",$outer,":",$replacement,";";
unset($outer,$replacement);
''',
    'list-literal-cv-review-detached-child-result-rebind': b'''<?php
function list_literal_cv_peer($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "W:",$n,":",($m==="Undefined array key 0"),":",$l,";";
    $GLOBALS["x"]=99;$GLOBALS["q"]=33;
    $GLOBALS["row"]=[0=>22,1=>66];
    $GLOBALS["row"]=&$GLOBALS["row_replacement"];
    unset($GLOBALS["outer"],$GLOBALS["outer_alias"],$GLOBALS["key"],$GLOBALS["key_alias"],$GLOBALS["q"]);
    $GLOBALS["outer"]=&$GLOBALS["outer_replacement"];
    $GLOBALS["key"]=&$GLOBALS["key_replacement"];
    $GLOBALS["next"]=1;
    return true;
}
$outer=0;$outer_alias=&$outer;$outer_replacement=7;
$key=false;$key_alias=&$key;$key_replacement="new";$next=2;
$q=2;$row=[1=>&$q,2=>6];$row_replacement=[0=>88,1=>99];
$x=7;$y=8;$tail=9;$dest=100;$calls=0;
set_error_handler("list_literal_cv_peer");
$dest=([
$outer=>[
$key=>$x,
$next=>$y
],
1=>$tail
]=[0=>&$row,1=>4]);
restore_error_handler();
echo "R:",($x===null),":",$y,":",$tail,":",$dest[0][1],":",$row[1],":",$row_replacement[1],":",$key,":",$key_replacement,":",$outer,":",isset($q),":",$calls,";";
$y=55;$dest[0][1]=77;$key="later";
echo "A:",$y,":",$dest[0][1],":",$row[1],":",$key,":",$key_replacement,";";
unset($dest,$row,$row_replacement,$key,$key_replacement,$outer,$outer_replacement);
echo "U:",isset($dest),":",isset($row),":",isset($key_alias),":",isset($outer_alias),";";
''',
}
