"""Integer key capture across cell retirement and later same-CV key reads."""

CASES = {
    'list-integer-cv-review-key-cell-retire': b'''<?php
function list_integer_cv_peer($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "W:",$n,":",($m==="Undefined array key -7"),":",$l,":",$GLOBALS["key"],";";
    $GLOBALS["x"]=99;$GLOBALS["key_alias"]=9;
    unset($GLOBALS["key"],$GLOBALS["key_alias"]);
    $GLOBALS["key"]=&$GLOBALS["replacement"];
    $GLOBALS["next"]=2;$GLOBALS["a"][-7]=77;
    return true;
}
$key=-7;$key_alias=&$key;$replacement=4;$next=1;$value=22;
$a=[1=>11,2=>$value];$x=7;$y=8;$dest=100;$calls=0;
set_error_handler("list_integer_cv_peer");
$dest=([
$key=>$x,
$next=>$y
]=
$a);
restore_error_handler();
echo "R:",($x===null),":",$y,":",$key,":",$replacement,":",$a[-7],":",isset($dest[-7]),":",$dest[1],":",$calls,";";
$key=8;
echo "A:",$key,":",$replacement,":",$y,";";
unset($dest,$a,$key,$replacement);
echo "U:",isset($key),":",isset($key_alias),":",isset($dest),";";
''',
    'list-integer-cv-review-prior-store-later-reference': b'''<?php
function list_integer_cv_peer($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "H:",$l,":",($m==="Undefined array key 1"),":",$GLOBALS["key"],":",$GLOBALS["missing"],":",$GLOBALS["late"],";";
    $GLOBALS["first"]=2;$GLOBALS["key"]=2;
    $GLOBALS["missing"]=99;$GLOBALS["q"]=33;
    return false;
}
error_reporting(0);$first=0;$key=9;$q=2;$a=[0=>1,2=>&$q];$copy=$a;
$missing=12;$late=13;$dest=100;$calls=0;
set_error_handler("list_integer_cv_peer",E_WARNING);
$dest=(list(
$first=>$key,
$key=>$missing,
$key=>&$late
)=
$a);
restore_error_handler();
echo "R:",$key,":",$first,":",($missing===null),":",$late,":",$a[0],":",$copy[0],":",$dest[0],":",$calls,";";
$late=44;$key=5;
echo "A:",$q,":",$a[2],":",$dest[2],":",$copy[2],":",$key,":",$first,";";
unset($dest,$a,$copy,$q,$late);
echo "U:",isset($dest),":",isset($a),":",isset($copy),":",isset($late),";";
''',
}
