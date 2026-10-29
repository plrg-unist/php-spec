"""A BYVAL factory returns a temporary BYREF Generator with only a weak observer."""

NORMAL = b'''<?php
function &factoryReferenceBodyNormal76() {
    $option="precision";echo "Y0;";yield 0=>$option;
    $value=7;echo "Y1;";yield 1=>$value;
    $value=8;ini_set("precision","6");echo "T;";
}
function factoryReferenceNormal76() {
    $gen=factoryReferenceBodyNormal76();
    $GLOBALS["watch"]=WeakReference::create($gen);
    echo "P;";
    return $gen;
}
ini_set("precision","14");$result=99;$watch=null;echo "B;";
$result=ini_set(...factoryReferenceNormal76());
echo "A:",$result,":",ini_get("precision"),":",
    (int)($watch->get()===null),";";
echo "R:",ini_set("precision","9"),":",ini_get("precision"),";";
unset($watch,$result);
'''

TERMINAL_THROW = b'''<?php
function &factoryReferenceBodyThrow76() {
    global $saved;
    $option="precision";echo "Y0;";yield 0=>$option;
    $value=7;echo "Y1;";yield 1=>$value;
    $value=8;ini_set("precision","6");echo "T;";throw $saved;
}
function factoryReferenceThrow76() {
    $gen=factoryReferenceBodyThrow76();
    $GLOBALS["watch"]=WeakReference::create($gen);
    echo "P;";
    return $gen;
}
ini_set("precision","14");$saved=new Exception("factory-reference-stop76");
$result=99;$watch=null;echo "B;";
try {$result=ini_set(...factoryReferenceThrow76());echo "BAD;";}
catch (Exception $caught) {
    echo "C:",(int)($caught===$saved),":",
        (int)($caught->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($watch->get()===null),";";
}
echo "R:",ini_set("precision","9"),":",ini_get("precision"),";";
unset($watch,$caught,$saved,$result);
'''

CASES = {
    'config-generator-factory-reference-normal': NORMAL,
    'config-generator-factory-reference-terminal-throw': TERMINAL_THROW,
}

EXPECTED = {
    'config-generator-factory-reference-normal':
        b'B;P;Y0;Y1;T;A:6:7:1;R:7:9;',
    'config-generator-factory-reference-terminal-throw':
        b'B;P;Y0;Y1;T;C:1:1:99:6:1;R:6:9;',
}
