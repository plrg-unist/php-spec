"""Mixed ordinary CV retargets balance pre-conversion table increments."""

CASES = {
    'array-literal-float-mixed-cv-array-scalar-array': b'''<?php
function literal_mixed_array_scalar($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {$GLOBALS["q"]=44;}
    else {$GLOBALS["q"]=$GLOBALS["old_hold"];}
    $GLOBALS["key"]=9.5;$GLOBALS["tail"]=66;return true;
}
$seed=2;$q=[$seed];$old_hold=$q;$key=1.5;$tail=7;$phase=0;
set_error_handler("literal_mixed_array_scalar",E_DEPRECATED);
$a=[
0=>9,
$key=>$q,
4=>$tail
];
echo "R:",$q,":",$a[1],":",$old_hold[0],":",$a[4],":",$key,":",$phase,";";
$key=3.5;
$b=[
$key=>$q
];
restore_error_handler();unset($old_hold);$q[0]=55;$copy=$b;$copy[3][0]=77;
echo "B:",$q[0],":",$b[3][0],":",$copy[3][0],":",$a[1],":",$phase,";";
unset($a,$b,$q,$copy,$key);
echo "U:",isset($q),":",isset($a),":",isset($old_hold),";";
''',
    'array-literal-float-mixed-cv-scalar-array-scalar': b'''<?php
function literal_mixed_scalar_array($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {$GLOBALS["q"]=$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=99;}
    $GLOBALS["key"]=9.5;$GLOBALS["tail"]=66;return true;
}
$q=33;$seed=44;$replacement=[$seed];$key=1.5;$tail=7;$phase=0;
set_error_handler("literal_mixed_scalar_array",E_DEPRECATED);
$a=[
0=>9,
$key=>$q,
4=>$tail
];
unset($replacement);$q[0]=55;
echo "R:",$q[0],":",$a[1][0],":",$a[4],":",$key,":",$phase,";";
$key=3.5;
$b=[
$key=>$q
];
restore_error_handler();$copy=$a;$copy[1][0]=66;
echo "B:",$q,":",$b[3],":",$a[1][0],":",$copy[1][0],":",$a[4],":",$phase,";";
unset($a,$b,$q,$copy,$key);
echo "U:",isset($q),":",isset($a),":",isset($replacement),";";
''',
}
