"""Frozen originals for sole-DATA Generator cleanup with a surviving scalar alias."""

NORMAL = b'''<?php
function &outsideReferenceNormal74() {
    global $input,$value,$alias;
    $option="precision";echo "Y0;";yield 0=>$option;
    $input=17;
    $value=7;$alias=&$value;echo "Y1;";yield 1=>$value;
    $value=8;echo "T;";
}
ini_set("precision","14");$value=2;$alias=0;
$input=outsideReferenceNormal74();$watch=WeakReference::create($input);
$result=99;echo "B;";$result=ini_set(...$input);
echo "A:",$result,":",ini_get("precision"),":",
    (int)($watch->get()===null),":",$input,":",$value,":",$alias,";";
$alias=12;echo "R:",ini_set("precision","9"),":",ini_get("precision"),":",$value,";";
unset($input,$watch,$result,$alias,$value);
'''

TERMINAL_THROW = b'''<?php
function &outsideReferenceThrow74() {
    global $input,$value,$alias,$saved;
    $option="precision";echo "Y0;";yield 0=>$option;
    $input=17;
    $value=7;$alias=&$value;echo "Y1;";yield 1=>$value;
    $value=8;ini_set("precision","6");echo "T;";throw $saved;
}
ini_set("precision","14");$value=2;$alias=0;
$saved=new Exception("outside-reference-stop74");
$input=outsideReferenceThrow74();$watch=WeakReference::create($input);
$result=99;echo "B;";
try {$result=ini_set(...$input);echo "BAD;";}
catch (Exception $caught) {
    echo "C:",(int)($caught===$saved),":",
        (int)($caught->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($watch->get()===null),":",
        $input,":",$value,":",$alias,";";
}
$alias=12;echo "R:",ini_set("precision","9"),":",ini_get("precision"),":",$value,";";
unset($input,$watch,$result,$caught,$saved,$alias,$value);
'''

CASES = {
    'config-generator-reference-outside-alias-normal': NORMAL,
    'config-generator-reference-outside-alias-terminal-throw': TERMINAL_THROW,
}

EXPECTED = {
    'config-generator-reference-outside-alias-normal':
        b'B;Y0;Y1;T;A:14:7:1:17:8:8;R:7:9:12;',
    'config-generator-reference-outside-alias-terminal-throw':
        b'B;Y0;Y1;T;C:1:1:99:6:1:17:8:8;R:6:9:12;',
}
