"""Ordinary by-value array CVs expose table-count bias across float-key callbacks."""

CASES = {
    'array-literal-float-array-cv-retarget': b'''<?php
function literal_array_cv_retarget($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {$GLOBALS["q"]=$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=$GLOBALS["old_hold"];}
    $GLOBALS["key"]=9.5;$GLOBALS["tail"]=66;return true;
}
$seed=2;$q=[$seed];$old_hold=$q;$next=44;$replacement=[$next];$key=1.5;$tail=7;$phase=0;
set_error_handler("literal_array_cv_retarget",E_DEPRECATED);
$a=[
0=>9,
$key=>$q,
4=>$tail
];
unset($replacement);$q[0]=55;
echo "R:",$q[0],":",$a[1][0],":",$old_hold[0],":",$a[4],":",$key,":",$phase,";";
$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$q[0]=66;$a[1][0]=77;
echo "B:",$q[0],":",$old_hold[0],":",$balance[3][0],":",$a[1][0],":",$a[4],":",$phase,";";
unset($a,$balance,$q,$old_hold,$key);
echo "U:",isset($q),":",isset($a),":",isset($replacement),";";
''',
    'array-literal-float-array-cv-same-table': b'''<?php
function literal_array_cv_stable($n,$m,$f,$l) {
    echo "D:",$n,":",$l,";";
    unset($GLOBALS["q"]);$GLOBALS["q"]=$GLOBALS["old_hold"];
    $GLOBALS["key"]=9.5;$GLOBALS["tail"]=66;return true;
}
$seed=44;$q=[$seed];$old_hold=$q;$key=2.5;$tail=7;
set_error_handler("literal_array_cv_stable",E_DEPRECATED);
$a=[
$key=>$q,
4=>$tail
];
restore_error_handler();$q[0]=55;$copy=$a;$copy[2][0]=77;
echo "R:",$a[2][0],":",$old_hold[0],":",$q[0],":",$copy[2][0],":",$a[4],":",$key,";";
unset($a,$copy,$q,$old_hold,$key);
echo "U:",isset($q),":",isset($a),":",isset($old_hold),";";
''',
}
