"""Typed string leaves separate table bias, byte snapshots and property sources."""

CASES = {
    'array-literal-float-typed-string-alias-leaf-cv-shared': b'''<?php
class LiteralTypedStringLeaf31 {public string $slot="new";}
function literal_typed_string_shared($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {$GLOBALS["q"]=$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=$GLOBALS["old_hold"];}
    return true;
}
$box=new LiteralTypedStringLeaf31;$leaf=&$box->slot;$old_leaf="old";
$q=[&$old_leaf,7];$old_hold=$q;$replacement=[&$leaf,8];unset($leaf);$key=1.5;$phase=0;
set_error_handler("literal_typed_string_shared",E_DEPRECATED);
$a=[
$key=>$q
];
unset($replacement);$snapshot=$q[0];$q[1]=55;$q[0]=123;$coerced=$q[0]==="123";$q[0][0]="N";$mid=$q[0];
try {$q[0]=[];echo "BAD;";} catch (TypeError $bad) {echo "T:",$coerced,":",$box->slot==="N23",":",$q[0]==="N23",";";}
unset($bad);
echo "R:",$box->slot,":",$q[0],":",$a[1][0],":",$snapshot,":",$mid,":",$q[1],":",$a[1][1],":",$phase,";";
$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$copy=$a;$copy[1][0][1]="Y";$copy[1][1]=77;$q[1]=99;$q[0][0]="O";
echo "B:",$box->slot,":",$a[1][0],":",$copy[1][0],":",$snapshot,":",$mid,":",$a[1][1],":",$copy[1][1],":",$q[0],":",$old_hold[0],":",$balance[3][0],":",$q[1],":",$old_hold[1],":",$balance[3][1],":",$phase,";";
unset($a,$balance,$q,$old_hold,$copy,$box,$old_leaf,$snapshot,$mid,$coerced,$key);
echo "U:",isset($q),":",isset($a),":",isset($box),";";
''',
    'array-literal-float-typed-string-alias-leaf-cv-unset-property': b'''<?php
class LiteralUnsetStringLeaf31 {public string $slot="new";}
function literal_typed_string_unset($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {$GLOBALS["q"]=$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=$GLOBALS["old_hold"];}
    return true;
}
$box=new LiteralUnsetStringLeaf31;$leaf=&$box->slot;$old_leaf="old";
$q=[&$old_leaf,7];$old_hold=$q;$replacement=[&$leaf,8];unset($leaf);$key=1.5;$phase=0;
set_error_handler("literal_typed_string_unset",E_DEPRECATED);
$a=[
$key=>$q
];
unset($replacement);$snapshot=$q[0];$q[1]=55;unset($box->slot);
$copy=$a;$copy[1][0][0]="X";$copy[1][1]=77;$q[0][0]="N";
echo "R:",$q[0],":",$a[1][0],":",$copy[1][0],":",$snapshot,":",$q[1],":",$a[1][1],":",$copy[1][1],":",isset($box->slot),":",$phase,";";
$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$balanced=$a;$balanced[1][0][1]="Y";$balanced[1][1]=99;
echo "B:",$a[1][0],":",$copy[1][0],":",$balanced[1][0],":",$snapshot,":",$a[1][1],":",$copy[1][1],":",$balanced[1][1],":",$q[0],":",$balance[3][0],":",isset($box->slot),":",$phase,";";
unset($a,$balance,$q,$old_hold,$copy,$balanced,$box,$old_leaf,$snapshot,$key);
echo "U:",isset($q),":",isset($a),":",isset($box),";";
''',
}
