"""Typed child arrays keep constraints independently of outer table deficits."""

CASES = {
    'array-literal-float-typed-array-alias-leaf-cv-shared': b'''<?php
class LiteralTypedArrayBox {public array $slot;}
function literal_typed_array_shared($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {$GLOBALS["q"]=$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=$GLOBALS["old_hold"];}
    return true;
}
$old_seed=33;$new_seed=44;$old_leaf=[$old_seed];
$q=[&$old_leaf,7];$old_hold=$q;$old_snapshot=$old_leaf;
$box=new LiteralTypedArrayBox;$box->slot=[$new_seed];$new_leaf=&$box->slot;$replacement=[&$new_leaf,8];unset($new_leaf);$snapshot=$box->slot;
$key=1.5;$phase=0;
set_error_handler("literal_typed_array_shared",E_DEPRECATED);
$a=[
$key=>$q
];
unset($replacement);$q[1]=55;
try {$a[1][0]=99;} catch (TypeError $e) {echo "T:",$box->slot[0]===44,":",$a[1][0][0]===44,";";}
unset($e);$a[1][0][0]=55;
echo "R:",$q[0][0],":",$a[1][0][0],":",$box->slot[0],":",$snapshot[0],":",$q[1],":",$a[1][1],":",$phase,";";
$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$copy=$a;$copy[1][0][0]=66;$copy[1][1]=77;$q[1]=99;$q[0][0]=88;
echo "B:",$a[1][0][0],":",$copy[1][0][0],":",$box->slot[0],":",$snapshot[0],":",$a[1][1],":",$copy[1][1],":",$q[0][0],":",$old_hold[0][0],":",$balance[3][0][0],":",$q[1],":",$old_hold[1],":",$balance[3][1],":",$old_snapshot[0],":",$phase,";";
unset($a,$balance,$q,$old_hold,$copy,$old_leaf,$snapshot,$old_snapshot,$box,$key,$old_seed,$new_seed);
echo "U:",isset($q),":",isset($a),":",isset($old_leaf),":",isset($box),";";
''',
    'array-literal-float-typed-array-alias-leaf-cv-unset-property': b'''<?php
class LiteralUnsetArrayBox {public array $slot;}
function literal_typed_array_unset($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {$GLOBALS["q"]=$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=$GLOBALS["old_hold"];}
    return true;
}
$old_seed=33;$new_seed=44;$old_leaf=[$old_seed];
$q=[&$old_leaf,7];$old_hold=$q;$old_snapshot=$old_leaf;
$box=new LiteralUnsetArrayBox;$box->slot=[$new_seed];$new_leaf=&$box->slot;$replacement=[&$new_leaf,8];unset($new_leaf);$snapshot=$box->slot;
$key=1.5;$phase=0;
set_error_handler("literal_typed_array_unset",E_DEPRECATED);
$a=[
$key=>$q
];
unset($replacement,$box->slot);$copy=$a;$copy[1][0][0]=55;$copy[1][1]=77;$q[0][0]=66;$q[1]=55;
echo "R:",$q[0][0],":",$a[1][0][0],":",$copy[1][0][0],":",$snapshot[0],":",isset($box->slot),":",$q[1],":",$copy[1][1],":",$phase,";";
$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$a[1][0]=99;$copy[1][0][0]=77;$q[1]=99;$q[0][0]=88;
echo "B:",$a[1][0],":",$copy[1][0][0],":",isset($box->slot),":",$snapshot[0],":",$a[1][1],":",$copy[1][1],":",$q[0][0],":",$old_hold[0][0],":",$balance[3][0][0],":",$q[1],":",$old_hold[1],":",$balance[3][1],":",$old_snapshot[0],":",$phase,";";
unset($a,$balance,$q,$old_hold,$copy,$old_leaf,$snapshot,$old_snapshot,$box,$key,$old_seed,$new_seed);
echo "U:",isset($q),":",isset($a),":",isset($old_leaf),":",isset($box),";";
''',
}
