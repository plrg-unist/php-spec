"""Typed embedded leaves keep property constraints separate from table counts."""

CASES = {
    'array-literal-float-typed-alias-leaf-cv-shared': b'''<?php
class LiteralTypedLeaf30 {public int $slot=44;}
function literal_typed_alias_shared($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {$GLOBALS["q"]=$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=$GLOBALS["old_hold"];}
    return true;
}
$box=new LiteralTypedLeaf30;$leaf=&$box->slot;$old_leaf=33;
$q=[&$old_leaf,7];$old_hold=$q;$replacement=[&$leaf,8];unset($leaf);$key=1.5;$phase=0;
set_error_handler("literal_typed_alias_shared",E_DEPRECATED);
$a=[
$key=>$q
];
unset($replacement);$q[1]=55;$q[0]="55";
try {$q[0]=[];echo "BAD;";} catch (TypeError $bad) {echo "T:",$box->slot===55,":",$q[0]===55,";";}
unset($bad);
echo "R:",$box->slot,":",$q[0],":",$a[1][0],":",$q[1],":",$a[1][1],":",$phase,";";
$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$copy=$a;$copy[1][0]="66";$copy[1][1]=77;
echo "B:",$box->slot,":",$a[1][0],":",$copy[1][0],":",$copy[1][0]===66,":",$a[1][1],":",$copy[1][1],":",$q[0],":",$old_hold[0],":",$balance[3][0],":",$phase,";";
unset($a,$balance,$q,$old_hold,$copy,$box,$old_leaf,$key);
echo "U:",isset($q),":",isset($a),":",isset($box),";";
''',
    'array-literal-float-typed-alias-leaf-cv-unset-property': b'''<?php
class LiteralUnsetLeaf30 {public int $slot=44;}
function literal_typed_alias_unset($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {$GLOBALS["q"]=$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=$GLOBALS["old_hold"];}
    return true;
}
$box=new LiteralUnsetLeaf30;$leaf=&$box->slot;$old_leaf=33;
$q=[&$old_leaf,7];$old_hold=$q;$replacement=[&$leaf,8];unset($leaf);$key=1.5;$phase=0;
set_error_handler("literal_typed_alias_unset",E_DEPRECATED);
$a=[
$key=>$q
];
unset($replacement);$q[1]=55;unset($box->slot);
$copy=$a;$copy[1][0]="free";$copy[1][1]=77;
echo "R:",$q[0],":",$a[1][0],":",$copy[1][0],":",$q[1],":",$a[1][1],":",$copy[1][1],":",isset($box->slot),":",$phase,";";
$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$balanced=$a;$balanced[1][0]=66;$balanced[1][1]=99;
echo "B:",$a[1][0],":",$copy[1][0],":",$balanced[1][0],":",$a[1][1],":",$copy[1][1],":",$balanced[1][1],":",$q[0],":",$balance[3][0],":",isset($box->slot),":",$phase,";";
unset($a,$balance,$q,$old_hold,$copy,$balanced,$box,$old_leaf,$key);
echo "U:",isset($q),":",isset($a),":",isset($box),";";
''',
}
