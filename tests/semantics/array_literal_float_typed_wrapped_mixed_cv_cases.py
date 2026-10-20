"""Typed captured slots preserve DIRECT values across primitive/array cycles."""

CASES = {
    'array-literal-float-typed-wrapped-mixed-cv-scalar-first': b'''<?php
class MixedSlot {public int|array $slot;}
function typed_wrapped_scalar($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {
        try {$GLOBALS["outside"]="bad";} catch (TypeError $e) {echo "T:",$GLOBALS["outside"]===2,":",$GLOBALS["box"]->slot===2,";";}
        $GLOBALS["outside"]=$GLOBALS["replacement"];
    } else {$GLOBALS["outside"]="44";echo "C:",$GLOBALS["outside"]===44,":",$GLOBALS["box"]->slot===44,";";}
    $GLOBALS["q"]=&$GLOBALS["other"];
    $GLOBALS["key"]=9.5;$GLOBALS["tail"]=66;return true;
}
$box=new MixedSlot();$box->slot=2;$q=&$box->slot;$outside=&$q;$old_hold=$q;
$next=44;$replacement=[$next];$other=99;$key=1.5;$tail=7;$phase=0;
set_error_handler("typed_wrapped_scalar",E_DEPRECATED);
$a=[
0=>9,
$key=>$q,
4=>$tail
];
unset($replacement);$outside[0]=55;$copy=$a;$copy[1][0]=66;
echo "R:",$q,":",$outside[0],":",$box->slot[0],":",$a[1][0],":",$copy[1][0],":",$old_hold,":",$a[4],":",$key,":",$phase,";";
$q=&$outside;$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$shared=$a;$shared[1][0]=77;$outside=66;
echo "B:",$q,":",$outside,":",$box->slot,":",$balance[3],":",$balance[3]===44,":",$a[1][0],":",$shared[1][0],":",$copy[1][0],":",$old_hold,":",$phase,";";
unset($a,$copy,$shared,$balance,$q,$outside,$box,$other,$old_hold,$key);
echo "U:",isset($q),":",isset($a),":",isset($outside),":",isset($balance),":",isset($box),";";
''',
    'array-literal-float-typed-wrapped-mixed-cv-array-first': b'''<?php
class MixedSlot {public int|array $slot;}
function typed_wrapped_array($n,$m,$f,$l) {
    $GLOBALS["phase"]++;echo "D:",$n,":",$GLOBALS["phase"],":",$l,";";
    if ($GLOBALS["phase"]===1) {
        $GLOBALS["outside"]="44";echo "C:",$GLOBALS["outside"]===44,":",$GLOBALS["box"]->slot===44,";";
        try {$GLOBALS["outside"]="bad";} catch (TypeError $e) {echo "T:",$GLOBALS["outside"]===44,":",$GLOBALS["box"]->slot===44,";";}
    } else {$GLOBALS["outside"]=$GLOBALS["old_hold"];}
    $GLOBALS["q"]=&$GLOBALS["other"];
    $GLOBALS["key"]=9.5;$GLOBALS["tail"]=66;return true;
}
$seed=2;$box=new MixedSlot();$box->slot=[$seed,7];$q=&$box->slot;$outside=&$q;$old_hold=$q;
$other=99;$key=1.5;$tail=7;$phase=0;
set_error_handler("typed_wrapped_array",E_DEPRECATED);
$a=[
0=>9,
$key=>$q,
4=>$tail
];
$copy=$a;$copy[1]=55;$outside=66;
echo "R:",$q,":",$outside,":",$box->slot,":",$a[1],":",$copy[1],":",$old_hold[0],":",$a[4],":",$key,":",$phase,";";
$q=&$outside;$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$shared=$balance;$shared[3][0]=77;$outside[0]=88;
$balance_copy=$balance;$balance_copy[3][0]=99;
echo "B:",$q,":",$a[1],":",$copy[1],":",$outside[0],":",$box->slot[0],":",$old_hold[0],":",$balance[3][0],":",$shared[3][0],":",$balance_copy[3][0],":",$phase,";";
unset($a,$copy,$shared,$balance,$balance_copy,$q,$outside,$box,$other,$old_hold,$key);
echo "U:",isset($q),":",isset($a),":",isset($outside),":",isset($balance),":",isset($box),";";
''',
}
