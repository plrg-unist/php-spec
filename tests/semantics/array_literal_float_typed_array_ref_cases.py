"""Typed outer array references retain counts while copied values shed constraints."""

CASES = {
    'array-literal-float-typed-array-ref-singleton-copy': b'''<?php
class LiteralTypedArrayRef35 { public array $slot; }
function literal_typed_array_ref_singleton($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {$GLOBALS["q"][0]=33;$GLOBALS["q"]=&$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=&$GLOBALS["outside"];}
    $GLOBALS["key"]=9.5;return true;
}
$old_seed=2;$q=[$old_seed];$outside=&$q;$seed=44;
$box=new LiteralTypedArrayRef35;$box->slot=[$seed];$replacement=&$box->slot;$key=1.5;$calls=0;
set_error_handler("literal_typed_array_ref_singleton",E_DEPRECATED);
$a=[
0=>9,
$key=>&$q
];
unset($q,$replacement);$snapshot=$box->slot;$copy=$a;$copy[1][0]=55;
echo "X:",$box->slot[0],":",$a[1][0],":",$copy[1][0],":",$snapshot[0],":",$outside[0],":",$calls,";";
$copy[1]=99;
echo "F:",$copy[1],":",($copy[1]===99),";";
$q=&$box->slot;$key=3.5;
$balance=[
$key=>&$q
];
restore_error_handler();$shared=$a;
try {$shared[1]=99;echo "BAD;";}
catch (TypeError $bad) {echo "T:",($box->slot[0]===44),":",($shared[1][0]===44),";";}
unset($bad);$shared[1][0]=66;
echo "B:",$box->slot[0],":",$a[1][0],":",$shared[1][0],":",$copy[1],":",$snapshot[0],":",$q[0],":",$outside[0],":",$balance[3][0],":",$calls,";";
unset($a,$copy,$shared,$balance,$snapshot,$q,$outside,$box,$key);
echo "U:",isset($q),":",isset($box),";";
''',
    'array-literal-float-typed-array-ref-unset-source': b'''<?php
class LiteralTypedArrayDetach35 { public array $slot; }
function literal_typed_array_ref_detach($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {$GLOBALS["q"][0]=33;$GLOBALS["q"]=&$GLOBALS["replacement"];}
    else {$GLOBALS["q"]=&$GLOBALS["outside"];}
    $GLOBALS["key"]=9.5;return true;
}
$old_seed=2;$oldbox=new LiteralTypedArrayDetach35;$oldbox->slot=[$old_seed];$old_snapshot=$oldbox->slot;
$q=&$oldbox->slot;$outside=&$q;$seed=44;$newbox=new LiteralTypedArrayDetach35;$newbox->slot=[$seed];
$replacement=&$newbox->slot;$key=1.5;$calls=0;
set_error_handler("literal_typed_array_ref_detach",E_DEPRECATED);
$a=[
0=>9,
$key=>&$q
];
unset($replacement);unset($newbox->slot);$snapshot=$q;$copy=$a;$copy[1][0]=55;$copy[1]=99;$q[0]=66;
echo "R:",$a[1][0],":",$q[0],":",$copy[1],":",$snapshot[0],":",$oldbox->slot[0],":",$old_snapshot[0],":",isset($newbox->slot),":",$calls,";";
$key=3.5;
$balance=[
$key=>&$q
];
restore_error_handler();$shared=$a;$shared[1][0]=77;$a[1]=99;
try {$balance[3]=99;echo "BAD;";}
catch (TypeError $bad) {echo "T:",($oldbox->slot[0]===33),":",($balance[3][0]===33),";";}
unset($bad);$q[0]=88;
echo "B:",$a[1],":",$shared[1][0],":",$copy[1],":",$snapshot[0],":",$oldbox->slot[0],":",$q[0],":",$outside[0],":",$balance[3][0],":",$old_snapshot[0],":",isset($newbox->slot),":",$calls,";";
unset($a,$copy,$shared,$balance,$snapshot,$old_snapshot,$q,$outside,$oldbox,$newbox,$key);
echo "U:",isset($q),":",isset($oldbox),":",isset($newbox),";";
''',
}
