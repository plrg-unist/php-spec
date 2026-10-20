"""Pooled constant arrays keep their source value across NULL-key callbacks."""

CASES = {
    'array-literal-null-key-constant-array-repeated': b'''<?php
function null_constant_make($key) {
    $GLOBALS["produced"]++;echo "P:",$GLOBALS["produced"],";";
    $a=[
    0=>9,
    $key=>[2,7],
    4=>$GLOBALS["tail"]
    ];
    echo "L:",$GLOBALS["produced"],":",$key===null,";";return $a;
}
function null_constant_repeated_key($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    $GLOBALS["key"]=9;$GLOBALS["tail"]=66;return true;
}
$key=null;$tail=7;$calls=0;$produced=0;
set_error_handler("null_constant_repeated_key",E_DEPRECATED);
$a=null_constant_make($key);$a[""][0]=55;$copy=$a;$copy[""][1]=77;
echo "A:",$a[""][0],":",$a[""][1],":",$copy[""][0],":",$copy[""][1],":",$key,":",$calls,";";
$key=null;$tail=7;$b=null_constant_make($key);
restore_error_handler();
echo "B:",$b[""][0],":",$b[""][1],":",$calls,":",$produced,";";
$b[""][1]=88;
echo "R:",$a[""][0],":",$a[""][1],":",$copy[""][0],":",$copy[""][1],":",$b[""][0],":",$b[""][1],":",$a[4],":",$copy[4],":",$b[4],":",$key,":",$calls,":",$produced,";";
unset($a,$b,$copy,$key,$tail,$calls,$produced);
echo "U:",isset($a),":",isset($b),":",isset($copy),";";
''',
    'array-literal-null-key-constant-array-empty': b'''<?php
function null_constant_empty_key($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    $GLOBALS["key"]=9;$GLOBALS["tail"]=66;return true;
}
$key=null;$tail=7;$calls=0;
set_error_handler("null_constant_empty_key",E_DEPRECATED);
$a=[
0=>9,
$key=>[],
4=>$tail
];
restore_error_handler();$copy=$a;$copy[""][0]=55;$copy[4]=77;$a[""][0]=66;
$empty=[];
echo "R:",$a[""][0],":",$copy[""][0],":",isset($empty[0]),":",$a[4],":",$copy[4],":",$key,":",$calls,";";
unset($a,$copy,$empty,$key,$tail,$calls);
echo "U:",isset($a),":",isset($copy),":",isset($empty),";";
''',
}
