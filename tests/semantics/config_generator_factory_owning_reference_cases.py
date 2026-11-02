"""A BYVAL factory returns a BYREF Generator with an owning final local cell."""

BODY = b'''<?php
class FactoryOwningRef87 {public int $tag=4;}
function &factoryOwningRefBody87() {
    $option="precision";echo "Y0;";yield 0=>$option;
    $payload=new FactoryOwningRef87();
    $GLOBALS["payloadWatch"]=WeakReference::create($payload);
    echo "Y1;";yield 1=>$payload;
    $payload->tag=5;echo "M:",$payload->tag,";";
    echo "W:",(int)($GLOBALS["payloadWatch"]->get()!==null),";";
    ini_set("precision",6);echo "T;";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
}
function factoryOwningRef87() {
    $gen=factoryOwningRefBody87();
    $GLOBALS["genWatch"]=WeakReference::create($gen);
    echo "P;";
    return $gen;
}
ini_set("precision",14);$genWatch=null;$payloadWatch=null;
$result=99;$saved=new Exception("factory-owning-reference87");
'''

CALL = b'''echo "B;";
try {$result=ini_set(...factoryOwningRef87());echo "BAD;";}
catch (TypeError $error) {
    echo "E:",(int)($error->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        (int)($payloadWatch->get()===null),";";
    $trace=$error->getTrace();$arg=$trace[0]["args"][1];
    echo "A:",$trace[0]["args"][0],":",
        (int)($arg===$payloadWatch->get()),":",$arg->tag,";";
    unset($arg,$trace,$error);
} catch (Exception $caught) {
    echo "S:",(int)($caught===$saved),":",
        (int)($caught->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        (int)($payloadWatch->get()===null),";";
}
echo "U:",(int)($genWatch->get()===null),":",
    (int)($payloadWatch->get()===null),";";
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($caught,$saved,$genWatch,$payloadWatch,$result,$mode);
'''

CASES = {
    'config-generator-factory-owning-reference-object-typeerror':
        BODY + b'$mode="normal";\n' + CALL,
    'config-generator-factory-owning-reference-object-terminal-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;P;Y0;Y1;M:5;W:1;T;'
EXPECTED = {
    'config-generator-factory-owning-reference-object-typeerror':
        PREFIX + b'E:1:99:6:1:0;A:precision:1:5;U:1:1;R:6:9;',
    'config-generator-factory-owning-reference-object-terminal-throw':
        PREFIX + b'S:1:1:99:6:1:1;U:1:1;R:6:9;',
}
