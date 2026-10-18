"""Post-conversion lookup, retired key cells and ordered missing-key delivery."""

CASES = {
    'list-float-key-review-present-negative-retire': b'''<?php
function list_float_key_peer($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float -2.75 to int loses precision"),":",$l,":",$GLOBALS["x"],";";
    $GLOBALS["key_alias"]=17.5;
    unset($GLOBALS["key"],$GLOBALS["key_alias"]);
    $GLOBALS["key"]=&$GLOBALS["replacement"];
    $GLOBALS["q"]=33;
    unset($GLOBALS["q"]);
    $GLOBALS["q"]=&$GLOBALS["other"];$GLOBALS["q"]=44;
    $GLOBALS["a"]=[-2=>22,4=>60];$GLOBALS["next"]=4;
    $GLOBALS["x"]=99;$GLOBALS["dest"]=200;
    return true;
}
error_reporting(0);$key=-2.75;$key_alias=&$key;$replacement=9.5;$next=0;
$q=2;$other=8;$a=[-2=>&$q,4=>6];$x=7;$y=8;$dest=100;$calls=0;
set_error_handler("list_float_key_peer",E_DEPRECATED);
$dest=([
$key=>$x,
$next=>$y
]=$a);
restore_error_handler();
echo "R:",$x,":",$y,":",$dest[-2],":",$a[-2],":",$q,":",$other,":",$key,":",$replacement,":",$calls,";";
$dest[-2]=55;
echo "A:",$dest[-2],":",$a[-2],":",$q,":",$other,";";
unset($dest,$a,$q,$other,$key,$replacement);
echo "U:",isset($dest),":",isset($q),":",isset($key_alias),";";
''',
    'list-float-key-review-deprecated-then-missing': b'''<?php
function list_float_key_second($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "W:",$n,":",($m==="Undefined array key 0"),":",$l,":",$GLOBALS["x"],";";
    $GLOBALS["q"]=33;$GLOBALS["next"]=1;
    $GLOBALS["x"]=99;$GLOBALS["y"]=88;$GLOBALS["a"][0]=77;
    return false;
}
function list_float_key_first($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",($m==="Implicit conversion from float 0.75 to int loses precision"),":",$l,":",$GLOBALS["x"],";";
    $GLOBALS["key"]=3.5;$GLOBALS["next"]=2.5;
    $GLOBALS["x"]=77;$GLOBALS["dest"]=200;
    set_error_handler("list_float_key_second");
    return true;
}
error_reporting(0);$key=0.75;$next=2;$q=2;$a=[1=>&$q,2=>6];
$x=7;$y=8;$dest=100;$calls=0;
set_error_handler("list_float_key_first");
$dest=([
$key=>$x,
$next=>$y
]=$a);
restore_error_handler();
echo "R:",($x===null),":",$y,":",$dest[1],":",$a[0],":",$q,":",$calls,":",isset($dest[0]),";";
$y=55;$dest[1]=66;
echo "A:",$y,":",$q,":",$a[1],":",$dest[1],";";
unset($dest,$a,$q);
echo "U:",isset($dest),":",isset($a),":",isset($q),";";
''',
}
