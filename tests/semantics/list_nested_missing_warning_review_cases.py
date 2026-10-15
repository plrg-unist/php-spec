"""Outer missing nested targets and completed child line/result authority."""

CASES = {
    'list-nested-review-outer-null-child': b'''<?php
function list_nested_peer($n,$m,$f,$l) {
    echo "W:",$l,":",($m==="Undefined array key 0"),";";
    $GLOBALS["x"]=99;$GLOBALS["y"]=88;
    $GLOBALS["a"]=[0=>[11,22],1=>33];
    return true;
}
$q=3;$a=[1=>$q];$x=7;$y=8;$z=9;$dest=100;
set_error_handler("list_nested_peer");
$dest=([
[
$x,
$y
],
$z
]=
$a);
restore_error_handler();
echo "R:",($x===null),":",($y===null),":",$z,":",$dest[1],":",isset($dest[0]),":",$a[0][0],":",$a[1],";";
unset($dest);
echo "U:",isset($dest),";";
''',
    'list-nested-review-earlier-child-line': b'''<?php
function list_nested_peer($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "H:",$l,":",$GLOBALS["first"],":",$GLOBALS["missing"],":",$GLOBALS["last"],";";
    $GLOBALS["q"]=33;$GLOBALS["first"]=21;$GLOBALS["missing"]=99;
    $GLOBALS["a"]=[0=>[90],1=>91,2=>92];
    return false;
}
error_reporting(0);$calls=0;$q=2;$a=[0=>[0=>&$q],2=>4];$first=7;$missing=8;$last=9;$dest=100;
set_error_handler("list_nested_peer",E_WARNING);
$dest=(list(
list(
$first
),
$missing,
$last
)=
$a);
restore_error_handler();
echo "R:",$first,":",($missing===null),":",$last,":",$dest[0][0],":",$dest[2],":",$a[1],":",$a[2],":",$calls,";";
$q=55;
echo "A:",$dest[0][0],":",$first,":",$last,";";
unset($dest,$q);
echo "U:",isset($dest),":",isset($q),";";
''',
}
