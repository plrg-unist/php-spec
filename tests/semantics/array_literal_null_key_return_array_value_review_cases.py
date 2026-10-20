"""Sole-owned by-value ARRAY returns at NULL keys survive or retire once."""

CASES = {
    'array-literal-null-key-return-array-value-review-delete-entry': b'''<?php
function literal_null_return_array_delete_value() {
    $GLOBALS["made"]++;$seed=$GLOBALS["seed"];echo "P:",$GLOBALS["made"],":",$seed,";";
    return [$seed,8];
}
function literal_null_return_array_delete($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    $GLOBALS["seed"]=99;$GLOBALS["key"]=9;$GLOBALS["tail"]=66;return true;
}
$seed=2;$key=null;$tail=7;$made=0;$calls=0;
set_error_handler("literal_null_return_array_delete",E_DEPRECATED);
$a=[
0=>9,
$key=>literal_null_return_array_delete_value(),
4=>$tail
];
restore_error_handler();$copy=$a;$copy[""][0]=66;$copy[""][1]=99;
echo "C:",$a[""][0],":",$copy[""][0],":",$a[""][1],":",$copy[""][1],":",$a[4],":",$seed,":",$made,":",$calls,";";
unset($copy);unset($a[""]);
echo "R:",isset($a[""]),":",$a[0],":",$a[4],":",$seed,":",$key,":",$made,":",$calls,":",isset($copy),";";
unset($a,$key,$seed,$tail,$made,$calls);
echo "U:",isset($a),":",isset($copy),":",isset($seed),";";
''',
    'array-literal-null-key-return-array-value-review-supplied-throw': b'''<?php
function literal_null_return_array_throw_value() {
    $GLOBALS["made"]++;$seed=$GLOBALS["seed"];echo "P:",$GLOBALS["made"],":",$seed,";";
    return [$seed,8];
}
function literal_null_return_array_throw($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    $GLOBALS["seed"]=99;$GLOBALS["key"]=9;$GLOBALS["dest"]=99;throw $GLOBALS["second"];
}
$seed=2;$key=null;$made=0;$calls=0;$dest=100;$later=7;$second=new Exception("supplied");
set_error_handler("literal_null_return_array_throw",E_DEPRECATED);
try {
    $dest=[
    0=>9,
    ""=>8,
    $key=>literal_null_return_array_throw_value(),
    4=>$later++
    ];
    echo "N;";
} catch (Exception $e) {echo "C:",$e===$second,":",$e->getPrevious()===null,":",$dest,":",$later,";";}
restore_error_handler();unset($e);
echo "R:",$seed,":",$key,":",$made,":",$calls,":",$dest,":",$later,":",isset($e),";";
unset($key,$seed,$made,$calls,$dest,$later,$second);
echo "U:",isset($seed),":",isset($dest),":",isset($second),";";
''',
}
