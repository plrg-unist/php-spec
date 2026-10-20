"""Table debt, embedded array-reference counts and child-array COW are separate."""

CASES = {
    'array-literal-float-array-alias-leaf-cv-shared': b'''<?php
function literal_array_alias_shared($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {$GLOBALS["q"]=$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=$GLOBALS["old_hold"];}
    return true;
}
$old_seed=33;$new_seed=44;$old_leaf=[$old_seed];$new_leaf=[$new_seed];
$q=[&$old_leaf,7];$old_hold=$q;$replacement=[&$new_leaf,8];$snapshot=$new_leaf;$old_snapshot=$old_leaf;
$key=1.5;$phase=0;
set_error_handler("literal_array_alias_shared",E_DEPRECATED);
$a=[
$key=>$q
];
unset($replacement);$q[1]=55;
echo "R:",$q[1],":",$a[1][1],":",$q[0][0],":",$a[1][0][0],":",$snapshot[0],":",isset($new_leaf),":",$phase,";";
$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$copy=$a;$copy[1][0][0]=66;$copy[1][1]=77;$q[1]=99;$q[0][0]=88;
echo "B:",$a[1][0][0],":",$copy[1][0][0],":",$a[1][1],":",$copy[1][1],":",$q[0][0],":",$old_hold[0][0],":",$balance[3][0][0],":",$q[1],":",$old_hold[1],":",$balance[3][1],":",$new_leaf[0],":",$snapshot[0],":",$old_snapshot[0],":",$phase,";";
unset($a,$balance,$q,$old_hold,$copy,$old_leaf,$new_leaf,$snapshot,$old_snapshot,$key,$old_seed,$new_seed);
echo "U:",isset($q),":",isset($a),":",isset($old_leaf),":",isset($new_leaf),";";
''',
    'array-literal-float-array-alias-leaf-cv-singleton': b'''<?php
function literal_array_alias_singleton($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {$GLOBALS["q"]=$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=$GLOBALS["old_hold"];}
    return true;
}
$old_seed=33;$new_seed=44;$old_leaf=[$old_seed];$new_leaf=[$new_seed];
$q=[&$old_leaf,7];$old_hold=$q;$replacement=[&$new_leaf,8];$snapshot=$new_leaf;$old_snapshot=$old_leaf;
$key=1.5;$phase=0;unset($new_leaf);
set_error_handler("literal_array_alias_singleton",E_DEPRECATED);
$a=[
$key=>$q
];
unset($replacement);$q[1]=55;
echo "R:",$q[1],":",$a[1][1],":",$q[0][0],":",$a[1][0][0],":",$snapshot[0],":",isset($new_leaf),":",$phase,";";
$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$copy=$a;$copy[1][0][0]=66;$copy[1][1]=77;$q[1]=99;$q[0][0]=88;
echo "B:",$a[1][0][0],":",$copy[1][0][0],":",$a[1][1],":",$copy[1][1],":",$q[0][0],":",$old_hold[0][0],":",$balance[3][0][0],":",$q[1],":",$old_hold[1],":",$balance[3][1],":",isset($new_leaf),":",$snapshot[0],":",$old_snapshot[0],":",$phase,";";
unset($a,$balance,$q,$old_hold,$copy,$old_leaf,$new_leaf,$snapshot,$old_snapshot,$key,$old_seed,$new_seed);
echo "U:",isset($q),":",isset($a),":",isset($old_leaf),":",isset($new_leaf),";";
''',
}
