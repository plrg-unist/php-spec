"""Factory-created temporary BYVAL Generators copy quiet owning options."""

NORMAL = b'''<?php
class OwningTemporary78 {public int $value=4;}
function owningTemporaryBody78() {
    $payload=new OwningTemporary78();
    $GLOBALS["payloadWatch"]=WeakReference::create($payload);
    echo "Y0;";yield 0=>$payload;
    $payload->value=5;unset($payload);
    echo "Y1;";yield 1=>7;
    echo "T;";
}
function owningTemporaryFactory78() {
    $gen=owningTemporaryBody78();
    $GLOBALS["genWatch"]=WeakReference::create($gen);
    echo "P;";return $gen;
}
ini_set("precision",14);$genWatch=null;$payloadWatch=null;$result=99;echo "B;";
try {$result=ini_set(...owningTemporaryFactory78());echo "BAD;";}
catch (TypeError $error) {
    echo "C:",(int)($genWatch->get()===null),":",
        (int)($payloadWatch->get()!==null),":",$result,":",
        ini_get("precision"),";";
    $trace=$error->getTrace();$arg=$trace[0]["args"][0];
    echo "A:",(int)($arg===$payloadWatch->get()),":",$arg->value,";";
    unset($arg,$trace,$error);
}
echo "U:",(int)($payloadWatch->get()===null),";";
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($genWatch,$payloadWatch,$result);
'''

TERMINAL_THROW = b'''<?php
class OwningTemporaryThrow78 {public int $value=4;}
function owningTemporaryThrowBody78() {
    $payload=new OwningTemporaryThrow78();
    $GLOBALS["payloadWatch"]=WeakReference::create($payload);
    echo "Y0;";yield 0=>$payload;
    $payload->value=5;unset($payload);
    echo "Y1;";yield 1=>7;
    ini_set("precision",6);echo "T;";throw $GLOBALS["saved"];
}
function owningTemporaryThrowFactory78() {
    $gen=owningTemporaryThrowBody78();
    $GLOBALS["genWatch"]=WeakReference::create($gen);
    echo "P;";return $gen;
}
ini_set("precision",14);$saved=new Exception("owning-temporary-stop78");
$genWatch=null;$payloadWatch=null;$result=99;echo "B;";
try {$result=ini_set(...owningTemporaryThrowFactory78());echo "BAD;";}
catch (Exception $caught) {
    echo "C:",(int)($caught===$saved),":",
        (int)($caught->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        (int)($payloadWatch->get()===null),";";
}
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($caught,$saved,$genWatch,$payloadWatch,$result);
'''

CASES = {
    'config-generator-owning-temporary-normal': NORMAL,
    'config-generator-owning-temporary-terminal-throw': TERMINAL_THROW,
}

EXPECTED = {
    'config-generator-owning-temporary-normal':
        b'B;P;Y0;Y1;T;C:1:1:99:14;A:1:5;U:1;R:14:9;',
    'config-generator-owning-temporary-terminal-throw':
        b'B;P;Y0;Y1;T;C:1:1:99:6:1:1;R:6:9;',
}
