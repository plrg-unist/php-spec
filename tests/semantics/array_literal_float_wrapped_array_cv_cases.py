"""Wrapped by-value array CVs keep the captured CELL payload locator."""

CASES = {
    'array-literal-float-wrapped-array-cv-stable': b'''<?php
function wrapped_array_stable($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    $GLOBALS["q"]=&$GLOBALS["other"];
    $GLOBALS["key"]=9.5;$GLOBALS["tail"]=66;return true;
}
$seed=2;$q=[$seed];$outside=&$q;$old_hold=$q;$other=99;$key=1.5;$tail=7;$phase=0;
set_error_handler("wrapped_array_stable",E_DEPRECATED);
$a=[
0=>9,
$key=>$q,
4=>$tail
];
$outside[0]=55;$copy=$a;$copy[1][0]=66;
echo "R:",$q,":",$other,":",$outside[0],":",$a[1][0],":",$copy[1][0],":",$old_hold[0],":",$a[4],":",$key,":",$phase,";";
restore_error_handler();$shared=$a;$shared[1][0]=77;$old_hold[0]=88;
echo "B:",$q,":",$outside[0],":",$a[1][0],":",$shared[1][0],":",$copy[1][0],":",$old_hold[0],":",$phase,";";
unset($a,$copy,$shared,$q,$outside,$other,$old_hold,$key);
echo "U:",isset($q),":",isset($a),":",isset($outside),":",isset($old_hold),";";
''',
    'array-literal-float-wrapped-array-cv-cycle': b'''<?php
function wrapped_array_cycle($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {$GLOBALS["outside"]=$GLOBALS["replacement"];}
    else {$GLOBALS["outside"]=$GLOBALS["old_hold"];}
    $GLOBALS["q"]=&$GLOBALS["other"];
    $GLOBALS["key"]=9.5;$GLOBALS["tail"]=66;return true;
}
$seed=2;$q=[$seed,7];$outside=&$q;$old_hold=$q;$next=44;$replacement=[$next,8];$other=99;$key=1.5;$tail=7;$phase=0;
set_error_handler("wrapped_array_cycle",E_DEPRECATED);
$a=[
0=>9,
$key=>$q,
4=>$tail
];
unset($replacement);$outside[0]=55;$copy=$a;$copy[1][0]=66;
echo "R:",$q,":",$other,":",$outside[0],":",$a[1][0],":",$copy[1][0],":",$old_hold[0],":",$a[4],":",$key,":",$phase,";";
$q=&$outside;$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$shared=$a;$shared[1][0]=77;$outside[0]=88;
$balance_copy=$balance;$balance_copy[3][0]=99;
echo "B:",$q,":",$outside[0],":",$a[1][0],":",$shared[1][0],":",$copy[1][0],":",$old_hold[0],":",$balance[3][0],":",$balance_copy[3][0],":",$a[4],":",$phase,";";
unset($a,$copy,$shared,$balance,$balance_copy,$q,$outside,$other,$old_hold,$key);
echo "U:",isset($q),":",isset($a),":",isset($outside),":",isset($old_hold),";";
''',
}
