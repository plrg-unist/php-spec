"""Recursive NULL descent and completed deep-target compiler location."""

CASES = {
    'list-recursive-review-outer-null-chain': b'''<?php
function list_recursive_peer($n,$m,$f,$l) {
    echo "W:",$l,":",($m==="Undefined array key 0"),";";
    $GLOBALS["x"]=99;$GLOBALS["y"]=88;
    $GLOBALS["a"]=[0=>[[[11,22]]],1=>33];
    return true;
}
$q=3;$a=[1=>$q];$x=7;$y=8;$z=9;$dest=100;
set_error_handler("list_recursive_peer");
$dest=([
[
[
[
$x,
$y
]
]
],
$z
]=
$a);
restore_error_handler();
echo "R:",($x===null),":",($y===null),":",$z,":",$dest[1],":",isset($dest[0]),":",$a[0][0][0][0],":",$a[1],";";
unset($dest);
echo "U:",isset($dest),";";
''',
    'list-recursive-review-completed-deep-line': b'''<?php
function list_recursive_peer($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "H:",$l,":",$GLOBALS["first"],":",$GLOBALS["missing"],":",$GLOBALS["last"],";";
    $GLOBALS["q"]=33;$GLOBALS["first"]=21;$GLOBALS["missing"]=99;
    $GLOBALS["row"]=[[[11,22],60],70];
    return false;
}
error_reporting(0);$calls=0;$q=2;$leaf=[1=>&$q];$mid=[$leaf,6];$row=[$mid,7];$a=[[[5]],&$row,4];unset($leaf,$mid);
$first=7;$missing=8;$last=9;$near=10;$middle=11;$tail=12;$dest=100;
set_error_handler("list_recursive_peer",E_WARNING);
$dest=(list(
list(list(
$first
)),
list(
list(
list(
$missing,
$last
),
$near
),
$middle
),
$tail
)=
$a);
restore_error_handler();
echo "R:",$first,":",($missing===null),":",$last,":",$near,":",$middle,":",$tail,":",$dest[0][0][0],":",$dest[1][0][0][1],":",$row[0][0][1],":",$calls,";";
$row[0][0][1]=44;$q=55;
echo "A:",$dest[1][0][0][1],":",$last,":",$q,":",$first,";";
unset($dest,$a,$row,$q);
echo "U:",isset($dest),":",isset($row),";";
''',
}
