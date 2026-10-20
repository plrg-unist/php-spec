"""Table bias, embedded string references and byte snapshots stay distinct."""

CASES = {
    'array-literal-float-string-alias-leaf-cv-shared': b'''<?php
function literal_string_alias_shared($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {$GLOBALS["q"]=$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=$GLOBALS["old_hold"];}
    return true;
}
$old_leaf="old";$new_leaf="new";$q=[&$old_leaf,7];$old_hold=$q;$replacement=[&$new_leaf,8];
$key=1.5;$phase=0;
set_error_handler("literal_string_alias_shared",E_DEPRECATED);
$a=[
$key=>$q
];
unset($replacement);$snapshot=$q[0];$q[1]=55;$q[0][0]="N";
echo "R:",$q[0],":",$a[1][0],":",$snapshot,":",$new_leaf,":",$q[1],":",$a[1][1],":",$phase,";";
$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$copy=$a;$copy[1][0][1]="Y";$copy[1][1]=77;$q[1]=99;$q[0][0]="O";
echo "B:",$a[1][0],":",$copy[1][0],":",$a[1][1],":",$copy[1][1],":",$q[0],":",$old_hold[0],":",$balance[3][0],":",$q[1],":",$old_hold[1],":",$balance[3][1],":",$new_leaf,":",$snapshot,":",$phase,";";
unset($a,$balance,$q,$old_hold,$copy,$old_leaf,$new_leaf,$snapshot,$key);
echo "U:",isset($q),":",isset($a),":",isset($old_leaf),":",isset($new_leaf),";";
''',
    'array-literal-float-string-alias-leaf-cv-singleton': b'''<?php
function literal_string_alias_singleton($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {$GLOBALS["q"]=$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=$GLOBALS["old_hold"];}
    return true;
}
$old_leaf="old";$new_leaf="new";$q=[&$old_leaf,7];$old_hold=$q;$replacement=[&$new_leaf,8];
$key=1.5;$phase=0;unset($new_leaf);
set_error_handler("literal_string_alias_singleton",E_DEPRECATED);
$a=[
$key=>$q
];
unset($replacement);$snapshot=$q[0];$q[1]=55;$q[0][0]="N";
echo "R:",$q[0],":",$a[1][0],":",$snapshot,":",isset($new_leaf),":",$q[1],":",$a[1][1],":",$phase,";";
$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$copy=$a;$copy[1][0][1]="Y";$copy[1][1]=77;$q[1]=99;$q[0][0]="O";
echo "B:",$a[1][0],":",$copy[1][0],":",$a[1][1],":",$copy[1][1],":",$q[0],":",$old_hold[0],":",$balance[3][0],":",$q[1],":",$old_hold[1],":",$balance[3][1],":",isset($new_leaf),":",$snapshot,":",$phase,";";
unset($a,$balance,$q,$old_hold,$copy,$old_leaf,$snapshot,$key);
echo "U:",isset($q),":",isset($a),":",isset($old_leaf),":",isset($new_leaf),";";
''',
}
