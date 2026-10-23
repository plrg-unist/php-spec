"""Undefined ARRAY keys freeze empty-string keys while primitive CVs stay live."""

CASES = {
    'array-literal-undefined-key-live-value': b'''<?php
function literal_undefined_live($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    $GLOBALS["key"]=9;$GLOBALS["q"]=44;$GLOBALS["tail"]=66;return true;
}
$q=2;$tail=7;$calls=0;
set_error_handler("literal_undefined_live",E_WARNING|E_DEPRECATED);
echo "P;";
$a=[
0=>9,
$key =>
$q,
$key=>$tail
];
restore_error_handler();
echo "R:",$a[""],":",$a[9],":",$a[0],":",$q,":",$key,":",$calls,";";
$copy=$a;$copy[""]=55;
echo "C:",$a[""],":",$copy[""],":",$a[9],":",$copy[9],";";
unset($a,$copy,$q,$tail,$key,$calls);
echo "U:",isset($a),":",isset($copy),":",isset($key),";";
''',
    'array-literal-undefined-key-then-null': b'''<?php
function literal_undefined_then_null($n,$m,$f,$l) {
    $GLOBALS["calls"]++;echo "D:",$n,":",$GLOBALS["calls"],":",$l,";";
    if ($n===E_WARNING) {
        $GLOBALS["warnings"]++;$GLOBALS["q"]=44;$GLOBALS["key"]=null;
    } else {
        $GLOBALS["deprecated"]++;$GLOBALS["q"]=55;$GLOBALS["key"]=9;
    }
    return true;
}
$q=2;$calls=0;$warnings=0;$deprecated=0;
set_error_handler("literal_undefined_then_null",E_WARNING|E_DEPRECATED);
$a=[
0=>9,
$key =>
$q
];
echo "A:",$a[""],":",$q,":",$key===null,":",$warnings,":",$deprecated,";";
$b=[
0=>8,
$key =>
$q
];
restore_error_handler();
echo "R:",$a[""],":",$b[""],":",$q,":",$key,":",$warnings,":",$deprecated,":",$calls,";";
unset($a,$b,$q,$key,$calls,$warnings,$deprecated);
echo "U:",isset($a),":",isset($b),":",isset($key),";";
''',
}
