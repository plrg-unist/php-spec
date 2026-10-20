"""Outer typed-array reference counts control copying, constraints and child COW."""

CASES = {
    'array-literal-typed-array-ref-review-delete-entry': b'''<?php
class LiteralTypedArrayRefDelete35 { public array $slot; }
function literal_typed_array_ref_delete($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {$GLOBALS["q"][1]=33;$GLOBALS["q"]=&$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=&$GLOBALS["outside"];}
    $GLOBALS["key"]=9.5;return true;
}
$old_seed=2;$old_child=[$old_seed];$q=[$old_child,7];$outside=&$q;unset($old_child);
$box=new LiteralTypedArrayRefDelete35;$new_seed=44;$new_child=[$new_seed];$box->slot=[$new_child,8];
$replacement=&$box->slot;unset($new_child);$key=-2.75;$calls=0;
set_error_handler("literal_typed_array_ref_delete",E_DEPRECATED);
$a=[
0=>9,
$key=>&$q
];
unset($a[-2]);$probe=[&$q];unset($q,$replacement);$snapshot=$box->slot[0];
$copy=$probe;$copy[0][0][0]=55;$copy[0][1]=88;$free=$copy;$free[0]=99;
$box->slot[0][0]=66;$box->slot[1]=66;
echo "R:",$box->slot[0][0],":",$probe[0][0][0],":",$copy[0][0][0],":",$snapshot[0],":",$free[0],":",$box->slot[1],":",$copy[0][1],":",$outside[0][0],":",$outside[1],":",isset($q),":",isset($replacement),":",$calls,";";
$q=&$box->slot;$key=3.5;
$balance=[
$key=>&$q
];
restore_error_handler();$shared=$probe;
try {$shared[0]=99;echo "BAD;";}
catch (TypeError $write_error) {echo "T:",($box->slot[0][0]===66),":",($copy[0][0][0]===55),":",($free[0]===99),";";}
unset($write_error);$shared[0][0][0]=77;$shared[0][1]=99;
echo "B:",$box->slot[0][0],":",$probe[0][0][0],":",$shared[0][0][0],":",$copy[0][0][0],":",$snapshot[0],":",$free[0],":",$box->slot[1],":",$shared[0][1],":",$copy[0][1],":",$q[0][0],":",$balance[3][0][0],":",$q[1],":",$calls,";";
unset($a,$probe,$copy,$free,$shared,$q,$outside,$balance,$snapshot,$key,$box);
echo "U:",isset($q),":",isset($replacement),":",isset($box),":",isset($new_child),";";
''',
    'array-literal-typed-array-ref-review-supplied-throw': b'''<?php
class LiteralTypedArrayRefThrow35 { public array $slot; }
function literal_typed_array_ref_throw($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {$GLOBALS["q"][1]=33;$GLOBALS["q"]=&$GLOBALS["replacement"];$GLOBALS["key"]=9.5;$GLOBALS["dest"]=99;throw $GLOBALS["second"];}
    $GLOBALS["q"]=&$GLOBALS["outside"];$GLOBALS["key"]=9.5;return true;
}
$old_seed=2;$old_child=[$old_seed];$q=[$old_child,7];$outside=&$q;unset($old_child);
$left=new LiteralTypedArrayRefThrow35;$right=new LiteralTypedArrayRefThrow35;$new_seed=44;$new_child=[$new_seed];
$left->slot=[$new_child,8];$right->slot=&$left->slot;$replacement=&$left->slot;unset($new_child);$key=1.5;$calls=0;
$dest=100;$later=7;$second=new Exception("supplied");
set_error_handler("literal_typed_array_ref_throw",E_DEPRECATED);
try {
    $dest=[
    0=>9,
    1=>&$outside,
    $key=>&$q,
    4=>$later++
    ];
    echo "N;";
} catch (Exception $e) {echo "C:",$e===$second,":",$e->getPrevious()===null,":",$dest,":",$later,";";}
unset($e);$probe=[&$q];unset($q,$replacement);$copy=$probe;
try {$copy[0]=99;echo "BAD;";}
catch (TypeError $write_error) {echo "T:",($left->slot[0][0]===44),":",($right->slot[0][0]===44),":",($probe[0][0][0]===44),";";}
unset($write_error);$detached=$left->slot;$snapshot=$detached[0];$detached[0][0]=55;$detached[1]=88;
$left->slot[0][0]=66;$left->slot[1]=66;
echo "R:",$left->slot[0][0],":",$right->slot[0][0],":",$probe[0][0][0],":",$copy[0][0][0],":",$detached[0][0],":",$snapshot[0],":",$left->slot[1],":",$detached[1],":",$outside[0][0],":",$outside[1],":",isset($q),":",isset($replacement),":",$dest,":",$later,":",$calls,";";
$q=&$left->slot;$key=3.5;
$balance=[
$key=>&$q
];
restore_error_handler();$shared=$probe;$shared[0][0][0]=77;$shared[0][1]=99;
echo "B:",$left->slot[0][0],":",$right->slot[0][0],":",$probe[0][0][0],":",$copy[0][0][0],":",$shared[0][0][0],":",$detached[0][0],":",$snapshot[0],":",$left->slot[1],":",$detached[1],":",$q[0][0],":",$balance[3][0][0],":",$q[1],":",$dest,":",$later,":",$calls,";";
unset($probe,$copy,$detached,$shared,$q,$outside,$balance,$snapshot,$key,$left,$right,$second);
echo "U:",isset($q),":",isset($replacement),":",isset($left),":",isset($right),";";
''',
}
