"""NULL-key reset preserves captured typed sources and safe explicit detachment."""

CASES = {
    'array-literal-null-key-typed-wrapped-cv-review-delete-entry': b'''<?php
class NullTypedDeleteBox { public int|array $slot; }
function literal_null_typed_delete($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",($m==="Using null as an array offset is deprecated, use an empty string instead"),":",$GLOBALS["calls"],":",$l,";";
    try {$GLOBALS["outside"]="bad";} catch (TypeError $e) {echo "T:",$GLOBALS["outside"][0]===2,":",$GLOBALS["box"]->slot[1]===7,";";}unset($e);
    $GLOBALS["outside"][0]=55;$GLOBALS["outside"][1]=88;$GLOBALS["q"]=&$GLOBALS["other"];unset($GLOBALS["box"]->slot);
    $GLOBALS["key"]=9;$GLOBALS["tail"]=66;echo "H:",$GLOBALS["q"],":",$GLOBALS["outside"][0],":",$GLOBALS["outside"][1],":",isset($GLOBALS["box"]->slot),";";return true;
}
$seed=2;$box=new NullTypedDeleteBox();$box->slot=[$seed,7];unset($seed);$outside=&$box->slot;$q=&$outside;$other=99;$key=null;$tail=7;$calls=0;
set_error_handler("literal_null_typed_delete",E_DEPRECATED);
$a=[
0=>9,
$key=>$q,
4=>$tail
];
restore_error_handler();$copy=$a;$copy[""][0]=66;$copy[""][1]=99;$outside=99;
echo "R:",$q,":",$other,":",$outside,":",$a[""][0],":",$a[""][1],":",$copy[""][0],":",$copy[""][1],":",isset($box->slot),":",$key,":",$a[4],":",$calls,";";
unset($outside);unset($copy);unset($a[""]);
echo "B:",isset($outside),":",isset($copy),":",isset($a[""]),":",$q,":",$other,":",$a[0],":",$a[4],":",$calls,";";
unset($q,$other,$box,$a,$key,$tail,$calls);
echo "U:",isset($q),":",isset($outside),":",isset($box),":",isset($a),";";
''',
    'array-literal-null-key-typed-wrapped-cv-review-supplied-throw': b'''<?php
class NullTypedThrowBox { public int|array $slot; }
function literal_null_typed_throw($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",($m==="Using null as an array offset is deprecated, use an empty string instead"),":",$GLOBALS["calls"],":",$l,";";
    $GLOBALS["outside"]="44";echo "W:",$GLOBALS["outside"]===44,":",$GLOBALS["left"]->slot===44,":",$GLOBALS["right"]->slot===44,";";
    try {$GLOBALS["outside"]="bad";} catch (TypeError $e) {echo "T:",$GLOBALS["outside"]===44,":",$GLOBALS["right"]->slot===44,";";}unset($e);
    $GLOBALS["q"]=&$GLOBALS["other"];$GLOBALS["key"]=9;$GLOBALS["dest"]=99;
    echo "H:",$GLOBALS["q"],":",$GLOBALS["outside"],";";throw $GLOBALS["second"];
}
$seed=2;$left=new NullTypedThrowBox();$left->slot=[$seed,7];unset($seed);$right=new NullTypedThrowBox();$right->slot=&$left->slot;
$outside=&$left->slot;$q=&$outside;$other=99;$key=null;$calls=0;$dest=100;$later=7;$second=new Exception("supplied");
set_error_handler("literal_null_typed_throw",E_DEPRECATED);
try {
    $dest=[
    0=>9,
    ""=>8,
    $key=>$q,
    4=>$later++
    ];
    echo "N;";
} catch (Exception $e) {echo "C:",$e===$second,":",$e->getPrevious()===null,":",$dest,":",$later,":",$q,":",$other,":",$outside[0],":",$outside[1],":",$left->slot[0],":",$right->slot[1],";";}
restore_error_handler();unset($e);
echo "R:",$q,":",$other,":",$outside[0],":",$outside[1],":",$key,":",$calls,":",$dest,":",$later,":",isset($e),";";
unset($q,$outside,$other,$left,$right,$key,$calls,$dest,$later,$second);
echo "U:",isset($q),":",isset($outside),":",isset($left),":",isset($right),":",isset($second),";";
''',
}
