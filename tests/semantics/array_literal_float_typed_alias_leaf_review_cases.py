"""Two live property type sources survive outer reference copying and throw."""

CASES = {
    'array-literal-typed-alias-review-delete-entry': b'''<?php
class LiteralTypedLeafDelete30 { public int $slot=44; }
function literal_typed_leaf_delete($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {$GLOBALS["q"][1]=33;$GLOBALS["q"]=&$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=&$GLOBALS["outside"];}
    $GLOBALS["key"]=9.5;return true;
}
$left=new LiteralTypedLeafDelete30;$right=new LiteralTypedLeafDelete30;
$right->slot=&$left->slot;$leaf=&$left->slot;$replacement=[&$leaf,8];unset($leaf);
$old_leaf=2;$q=[&$old_leaf,7];$outside=&$q;unset($old_leaf);$key=-2.75;$calls=0;
set_error_handler("literal_typed_leaf_delete",E_DEPRECATED);
$a=[
0=>9,
$key=>&$q
];
unset($a[-2]);$probe=[&$q];unset($q);$snapshot=$replacement[0];$copy=$probe;
try {$copy[0][0]=[];echo "BAD;";}
catch (TypeError $e) {echo "T:",($left->slot===44),":",($right->slot===44),":",($probe[0][0]===44),";";}
unset($e);$copy[0][0]="55";$copy[0][1]=88;$replacement[1]=66;
echo "R:",$left->slot,":",$right->slot,":",$replacement[0],":",$probe[0][0],":",$copy[0][0],":",($copy[0][0]===55),":",$replacement[1],":",$copy[0][1],":",$snapshot,":",$outside[0],":",$outside[1],":",isset($q),":",$calls,";";
$q=&$replacement;$key=3.5;
$balance=[
$key=>&$q
];
restore_error_handler();$shared=$probe;$shared[0][0]="77";$shared[0][1]=99;
echo "B:",$left->slot,":",$right->slot,":",$replacement[0],":",$probe[0][0],":",$shared[0][0],":",$copy[0][0],":",($left->slot===77),":",$replacement[1],":",$copy[0][1],":",$snapshot,":",$q[0],":",$balance[3][0],":",$q[1],":",$calls,";";
unset($a,$probe,$copy,$shared,$replacement,$q,$outside,$balance,$snapshot,$key,$left,$right);
echo "U:",isset($q),":",isset($replacement),":",isset($left),":",isset($right),";";
''',
    'array-literal-typed-alias-review-supplied-throw': b'''<?php
class LiteralTypedLeafThrow30 { public int $slot=44; }
function literal_typed_leaf_throw($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {$GLOBALS["q"][1]=33;$GLOBALS["q"]=&$GLOBALS["replacement"];$GLOBALS["key"]=9.5;$GLOBALS["dest"]=99;throw $GLOBALS["second"];}
    $GLOBALS["q"]=&$GLOBALS["outside"];$GLOBALS["key"]=9.5;return true;
}
$left=new LiteralTypedLeafThrow30;$right=new LiteralTypedLeafThrow30;
$right->slot=&$left->slot;$leaf=&$left->slot;$replacement=[&$leaf,8];unset($leaf);
$old_leaf=2;$q=[&$old_leaf,7];$outside=&$q;unset($old_leaf);$key=1.5;$calls=0;
$dest=100;$later=7;$second=new Exception("supplied");
set_error_handler("literal_typed_leaf_throw",E_DEPRECATED);
try {
    $dest=[
    0=>9,
    1=>&$outside,
    $key=>&$q,
    4=>$later++
    ];
    echo "N;";
} catch (Exception $e) {echo "C:",$e===$second,":",$e->getPrevious()===null,":",$dest,":",$later,";";}
unset($e);$probe=[&$q];unset($q);$snapshot=$replacement[0];$copy=$probe;
try {$copy[0][0]=[];echo "BAD;";}
catch (TypeError $write_error) {echo "T:",($left->slot===44),":",($right->slot===44),":",($probe[0][0]===44),";";}
unset($write_error);$copy[0][0]="55";$copy[0][1]=88;$replacement[1]=66;
echo "R:",$left->slot,":",$right->slot,":",$replacement[0],":",$probe[0][0],":",$copy[0][0],":",($copy[0][0]===55),":",$snapshot,":",$replacement[1],":",$copy[0][1],":",$outside[0],":",$outside[1],":",isset($q),":",$dest,":",$later,":",$calls,";";
$q=&$replacement;$key=3.5;
$balance=[
$key=>&$q
];
restore_error_handler();$shared=$probe;$shared[0][0]="77";$shared[0][1]=99;
echo "B:",$left->slot,":",$right->slot,":",$replacement[0],":",$probe[0][0],":",$shared[0][0],":",$copy[0][0],":",($left->slot===77),":",$snapshot,":",$replacement[1],":",$copy[0][1],":",$q[0],":",$balance[3][0],":",$q[1],":",$dest,":",$later,":",$calls,";";
unset($probe,$copy,$shared,$replacement,$q,$outside,$balance,$snapshot,$key,$left,$right,$second);
echo "U:",isset($q),":",isset($replacement),":",isset($left),":",isset($right),";";
''',
}
