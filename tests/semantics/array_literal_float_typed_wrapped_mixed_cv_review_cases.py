"""Typed captured slots keep their payload across deletion and supplied throw."""

CASES = {
    'array-literal-typed-wrapped-mixed-cv-review-delete-entry': b'''<?php
class LiteralTypedWrappedMixedDelete39 { public int|array $slot; }
function literal_typed_wrapped_mixed_delete($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {$GLOBALS["outside"]=$GLOBALS["replacement"];}
    else {$GLOBALS["outside"]=null;}
    $GLOBALS["q"]=&$GLOBALS["unrelated"];$GLOBALS["key"]=9.5;return true;
}
$box=new LiteralTypedWrappedMixedDelete39;$box->slot=2;
$q=&$box->slot;$outside=&$q;$initial=$q;
$next=44;$replacement=[$next,8];$unrelated=99;$key=-2.75;$calls=0;
set_error_handler("literal_typed_wrapped_mixed_delete",E_DEPRECATED);
$a=[
0=>9,
$key=>$q
];
unset($a[-2]);$outside[0]=55;$outside[1]=66;
$copy=$replacement;$copy[0]=66;$copy[1]=88;
try {$outside="bad";echo "BAD;";}
catch (TypeError $write_error) {echo "T:",$box->slot[0]===55,":",$outside[1]===66,";";}
unset($write_error);
echo "R:",$box->slot[0],":",$outside[0],":",$replacement[0],":",$copy[0],":",$outside[1],":",$replacement[1],":",$copy[1],":",$q,":",$initial,":",isset($a[-2]),":",$calls,";";
unset($box->slot);$q=&$outside;$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$replacement[0]=77;$shared=$replacement;$shared[0]=88;$shared[1]=99;$outside=77;
echo "B:",$replacement[0],":",$shared[0],":",$copy[0],":",$replacement[1],":",$shared[1],":",$copy[1],":",$outside,":",$balance[3]===null,":",isset($box->slot),":",$q,":",$unrelated,":",$calls,";";
unset($a,$copy,$shared,$replacement,$q,$outside,$balance,$key,$unrelated,$box);
echo "U:",isset($q),":",isset($outside),":",isset($replacement),":",isset($a),":",isset($balance),":",isset($box),";";
''',
    'array-literal-typed-wrapped-mixed-cv-review-supplied-throw': b'''<?php
class LiteralTypedWrappedMixedThrow39 { public int|array $slot; }
function literal_typed_wrapped_mixed_throw($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($GLOBALS["calls"]===1) {$GLOBALS["outside"]=$GLOBALS["replacement"];$GLOBALS["q"]=&$GLOBALS["unrelated"];$GLOBALS["key"]=9.5;$GLOBALS["dest"]=99;throw $GLOBALS["second"];}
    $GLOBALS["outside"]="44";$GLOBALS["q"]=&$GLOBALS["unrelated"];$GLOBALS["key"]=9.5;return true;
}
$left=new LiteralTypedWrappedMixedThrow39;$right=new LiteralTypedWrappedMixedThrow39;
$left->slot=2;$right->slot=&$left->slot;$q=&$left->slot;$outside=&$q;$initial=$q;
$next=44;$replacement=[$next,8];$unrelated=99;$key=1.5;$calls=0;
$dest=100;$later=7;$second=new Exception("supplied");
set_error_handler("literal_typed_wrapped_mixed_throw",E_DEPRECATED);
try {
    $dest=[
    0=>9,
    1=>8,
    $key=>$q,
    4=>$later++
    ];
    echo "N;";
} catch (Exception $e) {echo "C:",$e===$second,":",$e->getPrevious()===null,":",$dest,":",$later,";";}
unset($e);$outside[0]=55;$outside[1]=66;$copy=$replacement;$copy[0]=66;$copy[1]=88;
try {$outside="bad";echo "BAD;";}
catch (TypeError $write_error) {echo "T:",$left->slot[0]===55,":",$right->slot[1]===66,";";}
unset($write_error);
echo "R:",$left->slot[0],":",$right->slot[0],":",$outside[0],":",$replacement[0],":",$copy[0],":",$outside[1],":",$replacement[1],":",$copy[1],":",$q,":",$initial,":",$dest,":",$later,":",$calls,";";
$q=&$outside;$key=3.5;
$balance=[
$key=>$q
];
restore_error_handler();$replacement[0]=77;$shared=$replacement;$shared[0]=88;$shared[1]=99;$outside=77;
echo "B:",$replacement[0],":",$shared[0],":",$copy[0],":",$replacement[1],":",$shared[1],":",$copy[1],":",$left->slot,":",$right->slot,":",$outside,":",$balance[3],":",$balance[3]===44,":",$q,":",$unrelated,":",$dest,":",$later,":",$calls,";";
unset($copy,$shared,$replacement,$q,$outside,$balance,$key,$unrelated,$left,$right,$second);
echo "U:",isset($q),":",isset($outside),":",isset($replacement),":",isset($balance),":",isset($left),":",isset($right),":",isset($e),";";
''',
}
