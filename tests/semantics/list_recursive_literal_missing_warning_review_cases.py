"""Recursive literal NULL descent and saved row-cell authority."""

CASES = {
    'list-recursive-literal-review-outer-null-effect': b'''<?php
function list_recursive_literal_peer($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "W:",$n,":",($m==="Undefined array key 0"),":",$l,";";
    $GLOBALS["x"]=99;$GLOBALS["y"]=88;$GLOBALS["tail"]=77;
    return true;
}
$x=7;$y=8;$tail=9;$calls=0;
set_error_handler("list_recursive_literal_peer");
[
[
[
[
$x,
$y
]
]
],
$tail
]=[
1=>3
];
restore_error_handler();
echo "R:",($x===null),":",($y===null),":",$tail,":",$calls,";";
''',
    'list-recursive-literal-review-row-rebind': b'''<?php
function list_recursive_literal_peer($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "H:",$l,":",$GLOBALS["first"],":",$GLOBALS["missing"],":",$GLOBALS["last"],";";
    $GLOBALS["q"]=33;$GLOBALS["first"]=21;$GLOBALS["missing"]=99;
    $GLOBALS["row"]=[[[11,22],60],70];
    unset($GLOBALS["row"]);
    $GLOBALS["row"]=[[[55,66],600],700];
    return false;
}
error_reporting(0);$calls=0;$q=2;$leaf=[1=>&$q];$mid=[$leaf,6];$row=[$mid,7];unset($leaf,$mid);
$first=7;$missing=8;$last=9;$near=10;$middle=11;$tail=12;$dest=100;
set_error_handler("list_recursive_literal_peer",E_WARNING);
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
)=[
[[5]],
&$row,
4
]);
restore_error_handler();
echo "R:",$first,":",($missing===null),":",$last,":",$near,":",$middle,":",$tail,":",$dest[0][0][0],":",$dest[1][0][0][1],":",$row[0][0][1],":",$calls,";";
$row[0][0][1]=44;$q=55;
echo "A:",$dest[1][0][0][1],":",$row[0][0][1],":",$last,":",$first,";";
$dest[1][0][0][1]=88;
echo "B:",$dest[1][0][0][1],":",$row[0][0][1],":",$last,":",$q,";";
unset($dest,$row,$q);
echo "U:",isset($dest),":",isset($row),";";
''',
}
