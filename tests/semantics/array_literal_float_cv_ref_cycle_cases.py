"""Ordinary array CVs become references during float-key conversion."""

CASES = {
    'array-literal-float-cv-ref-cycle-primitive': b'''<?php
function literal_cv_ref_primitive($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {$GLOBALS["q"]=&$GLOBALS["replacement"];}
    else {unset($GLOBALS["q"]);$GLOBALS["q"]=$GLOBALS["old_hold"];}
    $GLOBALS["key"]=9.5;$GLOBALS["tail"]=66;return true;
}
$seed=2;$q=[$seed];$old_hold=$q;$replacement=44;$key=1.5;$tail=7;$phase=0;
set_error_handler("literal_cv_ref_primitive",E_DEPRECATED);
$a=[
0=>9,
$key=>$q,
4=>$tail
];
unset($q);$copy=$a;$copy[1]=55;$replacement=66;
echo "R:",$replacement,":",$a[1],":",$copy[1],":",$old_hold[0],":",$a[4],":",$key,":",$phase,";";
$q=&$replacement;$key=3.5;
$balance=[
$key=>&$q
];
restore_error_handler();$shared=$a;$shared[1]=77;$q[0]=88;
$balance_copy=$balance;$balance_copy[3][0]=99;
echo "B:",$replacement,":",$a[1],":",$shared[1],":",$copy[1],":",$q[0],":",$old_hold[0],":",$balance[3][0],":",$balance_copy[3][0],":",$a[4],":",$phase,";";
unset($a,$copy,$shared,$balance,$balance_copy,$q,$replacement,$old_hold,$key);
echo "U:",isset($q),":",isset($a),":",isset($replacement),":",isset($old_hold),";";
''',
    'array-literal-float-cv-ref-cycle-array': b'''<?php
function literal_cv_ref_array($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {$GLOBALS["q"]=&$GLOBALS["replacement"];}
    else {unset($GLOBALS["q"]);$GLOBALS["q"]=$GLOBALS["old_hold"];}
    $GLOBALS["key"]=9.5;$GLOBALS["tail"]=66;return true;
}
$seed=2;$q=[$seed];$old_hold=$q;$next=44;$replacement=[$next];$key=1.5;$tail=7;$phase=0;
set_error_handler("literal_cv_ref_array",E_DEPRECATED);
$a=[
0=>9,
$key=>$q,
4=>$tail
];
unset($q);$snapshot=$replacement;$copy=$a;$copy[1][0]=55;$replacement[0]=66;
echo "R:",$replacement[0],":",$a[1][0],":",$copy[1][0],":",$snapshot[0],":",$old_hold[0],":",$a[4],":",$key,":",$phase,";";
$q=&$replacement;$key=3.5;
$balance=[
$key=>&$q
];
restore_error_handler();$shared=$a;$shared[1][0]=77;$q[0]=88;
$balance_copy=$balance;$balance_copy[3][0]=99;
echo "B:",$replacement[0],":",$a[1][0],":",$shared[1][0],":",$copy[1][0],":",$snapshot[0],":",$q[0],":",$old_hold[0],":",$balance[3][0],":",$balance_copy[3][0],":",$a[4],":",$phase,";";
unset($a,$copy,$shared,$balance,$balance_copy,$q,$replacement,$snapshot,$old_hold,$key);
echo "U:",isset($q),":",isset($a),":",isset($replacement),":",isset($old_hold),";";
''',
}
