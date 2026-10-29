"""Generator scalar copies defer INI_SET reception until traversal finishes."""

VALUE_MATRIX = b'''<?php declare(strict_types=1);
function scalarValueGenerator71() {
    global $option,$value;
    echo "Y0;";yield 8=>$option;
    echo "Y1;";$option="serialize_precision";yield -4=>$value;
    echo "T;";$value="late";
}
$values=[null,false,true,17,17.5];
foreach ($values as $index=>$entry) {
    ini_set("precision","14");$option="precision";$value=$entry;
    $input=scalarValueGenerator71();$result=99;echo "B",$index,";";
    $result=ini_set(...$input);
    echo "A:",$result,":",ini_get("precision"),":",
        (int)($option==="serialize_precision"),":",(int)($value==="late"),";";
    ini_set("precision","14");unset($input,$option,$value,$result);
}
unset($values,$index,$entry);echo "U:",(int)isset($input),":",(int)isset($value),";";
'''

FLOAT_SNAPSHOT = b'''<?php
function scalarFloatGenerator71() {
    global $input,$call,$value;
    echo "Y0;";yield "0"=>"precision";
    echo "Y1;";$input=17;$call=ini_get(...);yield 1=>$value;
    echo "T:",ini_get("precision"),";";$value=4.5;
    ini_set("precision","3");echo "M:",ini_get("precision"),";";
}
$value=1.2345678901234567;$input=scalarFloatGenerator71();$hold=$input;
$watch=WeakReference::create($input);$call=ini_set(...);$keep=$call;$result=99;
echo "B;";$result=$call(...$input);
echo "A:",$result,":",ini_get("precision"),":",(int)($value===4.5),":",
    $input,":",$call("precision"),";";
unset($hold);echo "R:",(int)($watch->get()===null),";";
unset($input,$watch,$call,$keep,$value,$result);
echo "U:",(int)isset($input),":",(int)isset($value),";";
'''

STRICT_AND_THROW = b'''<?php declare(strict_types=1);
function strictScalarGenerator71() {
    global $option,$value,$abort;
    echo "Y0;";yield 0=>$option;
    echo "Y1;";yield 1=>$value;
    echo "T;";ini_set("precision","7");
    if ($abort) {throw $GLOBALS["saved"];}
}
$option=17.25;$value=13;$abort=false;$result=99;
$input=strictScalarGenerator71();echo "S;";
try {$result=ini_set(...$input);echo "BAD;";}
catch (TypeError $e) {
    echo "E:",(int)($e->getMessage()==='ini_set(): Argument #1 ($option) must be of type string, float given'),":",
        (int)($e->getPrevious()===null),":",$result,":",ini_get("precision"),";";
}
unset($input,$e);ini_set("precision","14");
$option="precision";$value=17;$abort=true;$result=99;
$saved=new Exception("scalar-stop71");$input=strictScalarGenerator71();echo "X;";
try {$result=ini_set(...$input);echo "BAD;";}
catch (Exception $e) {
    echo "C:",(int)($e===$saved),":",(int)($e->getPrevious()===null),":",
        $result,":",ini_get("precision"),";";
}
unset($input,$e,$saved,$option,$value,$abort,$result);
echo "U:",(int)isset($input),":",(int)isset($value),";";
'''

CASES = {
    'config-generator-scalar-strict-value-matrix': VALUE_MATRIX,
    'config-generator-scalar-float-post-terminal-precision': FLOAT_SNAPSHOT,
    'config-generator-scalar-strict-option-and-saved-terminal-throw': STRICT_AND_THROW,
}

EXPECTED = {
    'config-generator-scalar-strict-value-matrix':
        b''.join(b'B'+str(i).encode()+b';Y0;Y1;T;A:14:'+value+b':1:1;'
                 for i,value in enumerate([b'',b'',b'1',b'17',b'17.5']))+b'U:0:0;',
    'config-generator-scalar-float-post-terminal-precision':
        b'B;Y0;Y1;T:14;M:3;A:3:1.23:1:17:1.23;R:1;U:0:0;',
    'config-generator-scalar-strict-option-and-saved-terminal-throw':
        b'S;Y0;Y1;T;E:1:1:99:7;X;Y0;Y1;T;C:1:1:99:7;U:0:0;',
}
