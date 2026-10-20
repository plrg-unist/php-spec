"""Outer table counts and embedded primitive-reference counts stay separate."""

CASES = {
    'array-literal-float-alias-leaf-cv-shared': b'''<?php
function literal_alias_leaf_shared($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {$GLOBALS["q"]=$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=$GLOBALS["old_hold"];}
    return true;
}
$old_leaf=33;$new_leaf=44;$seed_a=7;$seed_b=8;$q=[&$old_leaf,$seed_a];$old_hold=$q;$replacement=[&$new_leaf,$seed_b];
$key=1.5;$phase=0;
set_error_handler("literal_alias_leaf_shared",E_DEPRECATED);
$a=[
$key=>$q
];
unset($replacement);$q[1]=55;
echo "R:",$q[1],":",$a[1][1],":",$q[0],":",$a[1][0],":",isset($new_leaf),":",$phase,";";
$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$copy=$a;$copy[1][0]=66;$copy[1][1]=77;$q[1]=99;$q[0]=88;
echo "B:",$a[1][0],":",$copy[1][0],":",$a[1][1],":",$copy[1][1],":",$q[0],":",$old_hold[0],":",$balance[3][0],":",$q[1],":",$old_hold[1],":",$balance[3][1],":",$new_leaf,":",$phase,";";
unset($a,$balance,$q,$old_hold,$copy,$old_leaf,$new_leaf,$key,$seed_a,$seed_b);
echo "U:",isset($q),":",isset($a),":",isset($old_leaf),":",isset($new_leaf),";";
''',
    'array-literal-float-alias-leaf-cv-singleton': b'''<?php
function literal_alias_leaf_singleton($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {$GLOBALS["q"]=$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=$GLOBALS["old_hold"];}
    return true;
}
$old_leaf=33;$new_leaf=44;$seed_a=7;$seed_b=8;$q=[&$old_leaf,$seed_a];$old_hold=$q;$replacement=[&$new_leaf,$seed_b];
$key=1.5;$phase=0;unset($new_leaf);
set_error_handler("literal_alias_leaf_singleton",E_DEPRECATED);
$a=[
$key=>$q
];
unset($replacement);$q[1]=55;
echo "R:",$q[1],":",$a[1][1],":",$q[0],":",$a[1][0],":",isset($new_leaf),":",$phase,";";
$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$copy=$a;$copy[1][0]=66;$copy[1][1]=77;$q[1]=99;$q[0]=88;
echo "B:",$a[1][0],":",$copy[1][0],":",$a[1][1],":",$copy[1][1],":",$q[0],":",$old_hold[0],":",$balance[3][0],":",$q[1],":",$old_hold[1],":",$balance[3][1],":",isset($new_leaf),":",$phase,";";
unset($a,$balance,$q,$old_hold,$copy,$old_leaf,$new_leaf,$key,$seed_a,$seed_b);
echo "U:",isset($q),":",isset($a),":",isset($old_leaf),":",isset($new_leaf),";";
''',
}
