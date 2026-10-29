"""Generator reference cells yield scalar argument snapshots before later writes."""

VALUE_MATRIX = b'''<?php declare(strict_types=1);
function &referenceScalarValueGenerator72() {
    global $option,$value;
    echo "Y0;";yield 8=>$option;
    echo "Y1;";$option="serialize_precision";yield -4=>$value;
    echo "T;";$value="late";
}
$values=[null,false,true,17,17.5];
foreach ($values as $index=>$entry) {
    ini_set("precision","14");$option="precision";$value=$entry;
    $input=referenceScalarValueGenerator72();$result=99;echo "B",$index,";";
    $result=ini_set(...$input);
    echo "A:",$result,":",ini_get("precision"),":",
        (int)($option==="serialize_precision"),":",(int)($value==="late"),";";
    ini_set("precision","14");unset($input,$option,$value,$result);
}
unset($values,$index,$entry);echo "U:",(int)isset($input),":",(int)isset($value),";";
'''

FLOAT_SNAPSHOT = b'''<?php
function &referenceScalarFloatGenerator72() {
    global $input,$call,$option,$value;
    echo "Y0;";yield 0=>$option;
    echo "Y1;";$option="serialize_precision";
    $input=17;$call=ini_get(...);yield 1=>$value;
    echo "T:",ini_get("precision"),";";$value=4.5;
    ini_set("precision","3");echo "M:",ini_get("precision"),";";
}
$option="precision";$value=1.2345678901234567;$valueAlias=&$value;
$input=referenceScalarFloatGenerator72();$hold=$input;
$watch=WeakReference::create($input);$call=ini_set(...);$keep=$call;$result=99;
echo "B;";$result=$call(...$input);
echo "A:",$result,":",ini_get("precision"),":",(int)($valueAlias===4.5),":",
    $option,":",$input,":",$call("precision"),";";
unset($hold);echo "R:",(int)($watch->get()===null),";";
unset($input,$watch,$call,$keep,$option,$value,$valueAlias,$result);
echo "U:",(int)isset($input),":",(int)isset($value),";";
'''

CASES = {
    'config-generator-reference-scalar-strict-value-matrix': VALUE_MATRIX,
    'config-generator-reference-scalar-float-live-alias-snapshot': FLOAT_SNAPSHOT,
}

EXPECTED = {
    'config-generator-reference-scalar-strict-value-matrix':
        b''.join(b'B'+str(i).encode()+b';Y0;Y1;T;A:14:'+value+b':1:1;'
                 for i,value in enumerate([b'',b'',b'1',b'17',b'17.5']))+b'U:0:0;',
    'config-generator-reference-scalar-float-live-alias-snapshot':
        b'B;Y0;Y1;T:14;M:3;A:3:1.23:1:serialize_precision:17:1.23;R:1;U:0:0;',
}
