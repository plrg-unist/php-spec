"""Mixed list source-cell identity, COW and earlier reference-line effects."""

CASES = {
    'list-reference-review-unset-rebind-cow': b'''<?php
function list_reference_peer($n,$m,$f,$l) {
    echo "W:",$l,":",$GLOBALS["copy"][1],";";
    unset($GLOBALS["a"]);
    $GLOBALS["a"] =& $GLOBALS["other"];
    $GLOBALS["a"][1]=44;
    return true;
}
$q=2;$a=[1=>$q];$copy=$a;$other=[1=>33];$x=7;$y=8;$dest=100;
set_error_handler("list_reference_peer");
$dest=([$x,&$y]=$a);
restore_error_handler();
echo "R:",($x===null),":",$y,":",$dest[1],":",$a[1],":",$other[1],":",$copy[1],":",isset($dest[0]),";";
$y=55;
echo "A:",$dest[1],":",$copy[1],":",$a[1],";";
unset($dest);
echo "B:",$y,";";
unset($y);
echo "U:",isset($y),":",$copy[1],";";
''',
    'list-reference-review-earlier-reference-line': b'''<?php
function list_reference_peer($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "H:",$l,":",$GLOBALS["first"],":",$GLOBALS["missing"],";";
    $GLOBALS["first"]=21;
    $GLOBALS["a"][3]=34;
    $GLOBALS["missing"]=99;
    return false;
}
error_reporting(0);$calls=0;$a=[0=>2,3=>4];$first=7;$missing=8;$last=9;$dest=100;
set_error_handler("list_reference_peer",E_WARNING);
$dest=(list(
&$first,
,
$missing,
&$last
)=
$a);
restore_error_handler();
echo "R:",$first,":",($missing===null),":",$last,":",$dest[0],":",$dest[3],":",isset($a[2]),":",$calls,";";
$first=22;$last=35;
echo "A:",$a[0],":",$dest[0],":",$a[3],":",$dest[3],";";
''',
}
