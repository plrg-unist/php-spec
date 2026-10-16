"""Detached nested cells and prior-reference compiler lines with array COW."""

CASES = {
    'list-nested-reference-review-detached-child-rebind': b'''<?php
function list_nested_reference_peer($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "W:",$n,":",($m==="Undefined array key 0"),":",$l,";";
    $GLOBALS["x"]=99;$GLOBALS["q"]=33;
    $GLOBALS["a"][0]=[1=>22];
    $GLOBALS["a"]=[[1=>66],44];
    unset($GLOBALS["a"],$GLOBALS["q"]);
    $GLOBALS["a"]=[[1=>77],55];
    return true;
}
$q=2;$a=[[1=>&$q],3];$x=7;$y=8;$tail=9;$dest=100;$calls=0;
set_error_handler("list_nested_reference_peer");
$dest=([
[$x,&$y],
$tail
]=
$a);
restore_error_handler();
echo "R:",($x===null),":",$y,":",$tail,":",$dest[0][1],":",$dest[1],":",$a[0][1],":",$a[1],":",isset($q),":",$calls,";";
$y=33;
echo "A:",$y,":",$dest[0][1],":",$a[0][1],";";
$dest[0][1]=88;$a[0][1]=99;
echo "B:",$y,":",$dest[0][1],":",$a[0][1],":",$tail,";";
unset($dest,$a,$y);
echo "U:",isset($dest),":",isset($a),":",isset($y),";";
''',
    'list-nested-reference-review-prior-reference-cow': b'''<?php
function list_nested_reference_peer($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "H:",$l,":",($m==="Undefined array key 1"),":",$GLOBALS["early"],":",$GLOBALS["missing"],":",$GLOBALS["late"],";";
    $GLOBALS["early"]=21;$GLOBALS["missing"]=99;$GLOBALS["q"]=33;
    return false;
}
error_reporting(0);$calls=0;$q=2;$leaf=[0=>5,2=>&$q];$mid=[$leaf,7];$a=[$mid,8];$copy=$a;unset($leaf,$mid);
$early=11;$missing=12;$late=13;$near=14;$tail=15;$dest=100;
set_error_handler("list_nested_reference_peer",E_WARNING);
$dest=(list(
list(
list(
&$early,
$missing,
&$late
),
$near
),
$tail
)=
$a);
restore_error_handler();
echo "R:",$early,":",($missing===null),":",$late,":",$near,":",$tail,":",$dest[0][0][0],":",$copy[0][0][0],":",$copy[0][0][2],":",$calls,";";
$early=55;$late=44;
echo "A:",$a[0][0][0],":",$dest[0][0][0],":",$copy[0][0][0],":",$a[0][0][2],":",$dest[0][0][2],":",$copy[0][0][2],":",$q,";";
unset($dest,$a,$copy,$q,$early,$late);
echo "U:",isset($dest),":",isset($a),":",isset($copy),":",isset($late),";";
''',
}
