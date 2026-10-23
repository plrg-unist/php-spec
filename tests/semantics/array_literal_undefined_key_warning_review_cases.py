"""Missing literal keys fix the empty key while primitive value CVs stay live."""

CASES = {
    'array-literal-undefined-key-review-default': b'''<?php
function literal_undefined_default($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "W:",$n,":",($m==='Undefined variable $missing'),":",$GLOBALS["calls"],":",$l,":",$GLOBALS["value"],";";
    $GLOBALS["missing"]=9;$GLOBALS["value"]=44;$GLOBALS["tail"]=66;return false;
}
$value=2;$tail=7;$calls=0;
set_error_handler("literal_undefined_default",E_ALL);
$a=[
0=>9,
$missing
=>
$value,
$missing=>$tail,
4=>$value
];
restore_error_handler();
echo "R:",$a[""],":",$a[9],":",$a[4],":",$missing,":",$value,":",$calls,";";
unset($a,$missing,$value,$tail,$calls);
echo "U:",isset($a),":",isset($missing),":",isset($value),";";
''',
    'array-literal-undefined-key-review-supplied-throw': b'''<?php
function literal_undefined_throw($n,$m,$f,$l) {
    $GLOBALS["calls"]++;
    echo "W:",$n,":",($m==='Undefined variable $offset'),":",$GLOBALS["calls"],":",$l,":",$GLOBALS["value"],";";
    $GLOBALS["offset"]=9;$GLOBALS["value"]=44;$GLOBALS["dest"]=99;throw $GLOBALS["second"];
}
$value=2;$calls=0;$dest=100;$later=7;$second=new Exception("supplied");
set_error_handler("literal_undefined_throw",E_ALL);
try {
    $dest=[
    0=>9,
    ""=>8,
    $offset
    =>
    $value,
    4=>$later++
    ];
    echo "N;";
} catch (Exception $e) {echo "C:",$e===$second,":",$e->getPrevious()===null,":",$dest,":",$later,":",$value,":",$offset,":",$calls,";";}
restore_error_handler();unset($e);
echo "R:",$value,":",$offset,":",$calls,":",$dest,":",$later,":",isset($e),";";
unset($offset,$value,$calls,$dest,$later,$second);
echo "U:",isset($value),":",isset($dest),":",isset($second),";";
''',
}
