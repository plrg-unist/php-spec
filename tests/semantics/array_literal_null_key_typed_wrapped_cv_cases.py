"""NULL-key reset of captured typed payloads, including snapshot compatibility."""

CASES = {
    'array-literal-null-key-typed-wrapped-cv-scalar': b'''<?php
class NullTypedScalar { public int|array $slot; }
function literal_null_typed_scalar($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,":",$GLOBALS["outside"],";";
    try {$GLOBALS["outside"]="bad";} catch(TypeError $e) {echo "T:",($GLOBALS["outside"]===2),":",($GLOBALS["box"]->slot===2),";";unset($e);}
    $GLOBALS["outside"]=[$GLOBALS["seed"],88];$GLOBALS["changed"]=$GLOBALS["outside"];$GLOBALS["q"]=&$GLOBALS["other"];
    $GLOBALS["key"]=9;$GLOBALS["tail"]=66;echo "H:",$GLOBALS["outside"][0],":",$GLOBALS["outside"][1],":",$GLOBALS["q"],";";return true;
}
$box=new NullTypedScalar;$box->slot=2;$q=&$box->slot;$outside=&$q;$initial=$outside;$seed=55;$other=99;$key=null;$tail=7;$calls=0;
set_error_handler("literal_null_typed_scalar",E_DEPRECATED);
$a=[
0=>9,
$key=>$q,
4=>$tail
];
restore_error_handler();$copy=$a;$copy[""]=55;
echo "R:",$outside,":",$box->slot,":",$q,":",$other,":",$a[""],":",$copy[""],":",$initial,":",$changed[0],":",$changed[1],":",$key,":",$a[4],":",$calls,";";
$outside=77;$q=88;echo "B:",$outside,":",$box->slot,":",$q,":",$other,":",$a[""],":",$copy[""],":",$initial,":",$changed[0],":",$changed[1],";";
unset($q,$outside,$box,$other,$initial,$seed,$changed,$a,$copy,$key,$tail,$calls);
echo "U:",isset($q),":",isset($outside),":",isset($box),":",isset($a),";";
''',
    'array-literal-null-key-typed-wrapped-cv-array': b'''<?php
class NullTypedArray { public int|array $slot; }
class NullTypedGuard { public int $slot; }
function literal_null_typed_array($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,":",$GLOBALS["outside"][0],";";
    $GLOBALS["outside"]="44";
    try {$GLOBALS["outside"]="bad";} catch(TypeError $e) {echo "T:",($GLOBALS["outside"]===44),":",($GLOBALS["box"]->slot===44),";";unset($e);}
    $GLOBALS["guard"]->slot=&$GLOBALS["outside"];echo "G:",$GLOBALS["guard"]->slot,":",($GLOBALS["outside"]===44),";";
    unset($GLOBALS["guard"]->slot);$GLOBALS["q"]=&$GLOBALS["other"];
    $GLOBALS["key"]=9;$GLOBALS["tail"]=66;echo "H:",$GLOBALS["outside"],":",$GLOBALS["q"],";";return true;
}
$seed=2;$box=new NullTypedArray;$box->slot=[$seed,7];$q=&$box->slot;$outside=&$q;$old_hold=$outside;$guard=new NullTypedGuard;$guard->slot=0;$other=99;$key=null;$tail=7;$calls=0;
set_error_handler("literal_null_typed_array",E_DEPRECATED);
$a=[
0=>9,
$key=>$q,
4=>$tail
];
restore_error_handler();$copy=$a;$copy[""][0]=66;
echo "R:",$outside[0],":",$outside[1],":",$box->slot[0],":",$q,":",$a[""][0],":",$a[""][1],":",$copy[""][0],":",$copy[""][1],":",$old_hold[0],":",$old_hold[1],":",$key,":",$a[4],":",$calls,";";
$outside[0]=77;$a[""][1]=99;$q=88;
echo "B:",$outside[0],":",$outside[1],":",$box->slot[0],":",$q,":",$other,":",$a[""][0],":",$a[""][1],":",$copy[""][0],":",$copy[""][1],":",$old_hold[0],":",$old_hold[1],":",isset($guard->slot),";";
unset($q,$outside,$box,$guard,$old_hold,$other,$seed,$a,$copy,$key,$tail,$calls);
echo "U:",isset($q),":",isset($outside),":",isset($box),":",isset($guard),":",isset($a),";";
''',
}
