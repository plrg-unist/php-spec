"""Direct child arrays keep their owners separately from literal table biases."""

CASES = {
    'array-literal-float-direct-array-leaf-cv-snapshot': b'''<?php
function literal_direct_child_snapshot($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {$GLOBALS["q"]=$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=$GLOBALS["old_hold"];}
    return true;
}
$old_seed=33;$new_seed=44;$old_inner=[$old_seed];$q=[$old_inner,7];$old_hold=$q;$old_snapshot=$old_inner;unset($old_inner);
$new_inner=[$new_seed];$replacement=[$new_inner,8];$snapshot=$new_inner;unset($new_inner);
$key=1.5;$phase=0;
set_error_handler("literal_direct_child_snapshot",E_DEPRECATED);
$a=[
$key=>$q
];
unset($replacement);$q[1]=55;$q[0][0]=66;
echo "R:",$q[0][0],":",$a[1][0][0],":",$snapshot[0],":",$q[1],":",$a[1][1],":",$phase,";";
$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$copy=$a;$copy[1][0][0]=77;$copy[1][1]=88;$q[1]=99;$q[0][0]=22;
echo "B:",$a[1][0][0],":",$copy[1][0][0],":",$snapshot[0],":",$a[1][1],":",$copy[1][1],":",$q[0][0],":",$old_hold[0][0],":",$balance[3][0][0],":",$old_snapshot[0],":",$q[1],":",$old_hold[1],":",$balance[3][1],":",$phase,";";
unset($a,$balance,$q,$old_hold,$copy,$snapshot,$old_snapshot,$key,$old_seed,$new_seed);
echo "U:",isset($q),":",isset($a),":",isset($copy),":",isset($snapshot),";";
''',
    'array-literal-float-direct-array-leaf-cv-repeated-child': b'''<?php
function literal_direct_child_repeated($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {$GLOBALS["q"]=$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=$GLOBALS["old_hold"];}
    return true;
}
$old_seed=33;$new_seed=44;$old_inner=[$old_seed];$q=[$old_inner,7];$old_hold=$q;$old_snapshot=$old_inner;unset($old_inner);
$new_inner=[$new_seed];$replacement=[$new_inner,$new_inner,8];unset($new_inner);
$key=1.5;$phase=0;
set_error_handler("literal_direct_child_repeated",E_DEPRECATED);
$a=[
$key=>$q
];
unset($replacement);$q[2]=55;$q[0][0]=66;
echo "R:",$q[0][0],":",$a[1][0][0],":",$q[1][0],":",$a[1][1][0],":",$q[2],":",$a[1][2],":",$phase,";";
$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$copy=$a;$copy[1][0][0]=77;$copy[1][1][0]=88;$copy[1][2]=99;$q[1]=99;$q[0][0]=22;
echo "B:",$a[1][0][0],":",$copy[1][0][0],":",$a[1][1][0],":",$copy[1][1][0],":",$a[1][2],":",$copy[1][2],":",$q[0][0],":",$old_hold[0][0],":",$balance[3][0][0],":",$old_snapshot[0],":",$q[1],":",$old_hold[1],":",$balance[3][1],":",$phase,";";
unset($a,$balance,$q,$old_hold,$copy,$old_snapshot,$key,$old_seed,$new_seed);
echo "U:",isset($q),":",isset($a),":",isset($copy),":",isset($new_inner),";";
''',
}
