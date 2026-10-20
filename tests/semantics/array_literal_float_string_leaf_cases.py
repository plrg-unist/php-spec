"""Table-count bias stays separate from copied string-leaf bytes."""

CASES = {
    'array-literal-float-string-leaf-cv-retarget': b'''<?php
function literal_string_leaf_retarget($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {$GLOBALS["q"]=$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=$GLOBALS["old_hold"];}
    $GLOBALS["key"]=9.5;$GLOBALS["tail"]=66;return true;
}
$old_seed="old";$q=[$old_seed];$old_hold=$q;$new_seed="new";$replacement=[$new_seed];$key=1.5;$tail=7;$phase=0;
set_error_handler("literal_string_leaf_retarget",E_DEPRECATED);
$a=[
0=>9,
$key=>$q,
4=>$tail
];
unset($replacement);$snapshot=$q[0];$q[0][0]="N";
echo "R:",$q[0],":",$a[1][0],":",$snapshot,":",$new_seed,":",$a[4],":",$key,":",$phase,";";
$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$q[0][0]="O";$copy=$a;$copy[1][0][1]="Y";
echo "B:",$q[0],":",$old_hold[0],":",$balance[3][0],":",$a[1][0],":",$copy[1][0],":",$snapshot,":",$phase,";";
unset($a,$balance,$q,$old_hold,$copy,$snapshot,$key,$old_seed,$new_seed);
echo "U:",isset($q),":",isset($a),":",isset($replacement),";";
''',
    'array-literal-float-string-leaf-cv-same-table': b'''<?php
function literal_string_leaf_stable($n,$m,$f,$l) {
    echo "D:",$n,":",$l,";";
    unset($GLOBALS["q"]);$GLOBALS["q"]=$GLOBALS["old_hold"];
    $GLOBALS["key"]=9.5;$GLOBALS["tail"]=66;return true;
}
$seed="new";$q=[$seed];$old_hold=$q;$key=2.5;$tail=7;
set_error_handler("literal_string_leaf_stable",E_DEPRECATED);
$a=[
$key=>$q,
4=>$tail
];
restore_error_handler();$snapshot=$a[2][0];$q[0][0]="N";$copy=$a;$copy[2][0][1]="Y";
echo "R:",$a[2][0],":",$old_hold[0],":",$q[0],":",$copy[2][0],":",$snapshot,":",$seed,":",$a[4],":",$key,";";
unset($a,$copy,$q,$old_hold,$snapshot,$seed,$key);
echo "U:",isset($q),":",isset($a),":",isset($old_hold),";";
''',
}
