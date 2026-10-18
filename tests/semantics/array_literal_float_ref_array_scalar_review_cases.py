"""Scalar retargets cancel an owning-cell debt or retain old-array multiplicity."""

CASES = {
    'array-literal-ref-array-scalar-review-cancel-debt': b'''<?php
function literal_array_scalar_peer_cancel($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {
        $GLOBALS["q"]=33;unset($GLOBALS["q"]);
        $GLOBALS["q"]=&$GLOBALS["replacement"];
    } else {
        $GLOBALS["replacement"][0]=66;unset($GLOBALS["q"]);
        $GLOBALS["q"]=99;
    }
    $GLOBALS["key"]=9.5;return true;
}
error_reporting(0);$q=2;$outside=&$q;$seed=44;$replacement=[$seed];
$key=1.5;$calls=0;
set_error_handler("literal_array_scalar_peer_cancel",E_DEPRECATED);
$a=[
0=>8,
$key=>&$q
];
$snapshot=$replacement;$key=3.5;
$b=[
$key=>&$q
];
restore_error_handler();unset($q,$replacement);$copy=$a;$copy[1][0]=55;$q=123;
echo "R:",$a[1][0],":",$copy[1][0],":",$snapshot[0],":",$b[3],":",$q,":",$outside,":",$calls,";";
$old_probe=[&$outside];unset($outside);$old_copy=$old_probe;$old_copy[0]=77;
echo "G:",$old_probe[0],":",$old_copy[0],";";
unset($a,$b,$snapshot,$copy,$q,$old_probe,$old_copy,$key,$seed);
echo "U:",isset($q),":",isset($a),":",isset($replacement),":",isset($outside),";";
''',
    'array-literal-ref-array-scalar-review-repeat-owners': b'''<?php
function literal_array_scalar_peer_repeat($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {
        $GLOBALS["q"][0]=31;unset($GLOBALS["q"]);$GLOBALS["q"]=41;
    } else {
        $GLOBALS["q"][0]=32;unset($GLOBALS["q"]);$GLOBALS["q"]=42;
    }
    $GLOBALS["key"]=9.5;return true;
}
error_reporting(0);$seed=2;$q=[$seed];$outside=&$q;$key=1.5;$calls=0;
set_error_handler("literal_array_scalar_peer_repeat",E_DEPRECATED);
$a=[
$key=>&$q
];
$q=&$outside;$key=2.5;
$b=[
$key=>&$q
];
restore_error_handler();$q=99;
$probe=[&$outside];unset($outside);$copy=$probe;$copy[0][0]=66;
echo "R:",$a[1],":",$b[2],":",$q,":",$probe[0][0],":",$copy[0][0],":",$calls,";";
unset($a,$b,$probe,$copy,$q,$key,$seed);
echo "U:",isset($q),":",isset($outside),":",isset($a),":",isset($b),";";
''',
}
