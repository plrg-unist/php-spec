"""A BYVAL factory returns a BYREF Generator with an owning first local cell."""

BODY = b'''<?php
class FactoryFirstOwning91 {public int $tag=4;}
function &factoryFirstBody91() {
    $payload=new FactoryFirstOwning91();
    $GLOBALS["payloadWatch"]=WeakReference::create($payload);
    echo "Y0;";yield 0=>$payload;
    $payload->tag=5;echo "M:",$payload->tag,";";
    $payload=9;echo "W:",(int)($GLOBALS["payloadWatch"]->get()!==null),";";
    if ($GLOBALS["mode"]==="early") {ini_set("precision",6);echo "T:early;";throw $GLOBALS["saved"];}
    $value=7;echo "Y1;";yield 1=>$value;
    $value=8;ini_set("precision",6);echo "T:",$value,";";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
}
function factoryFirstOwning91() {
    $gen=factoryFirstBody91();
    $GLOBALS["genWatch"]=WeakReference::create($gen);
    echo "P;";
    return $gen;
}
ini_set("precision",14);$genWatch=null;$payloadWatch=null;
$result=99;$saved=new Exception("factory-first-owning91");
'''

CALL = b'''echo "B;";
try {$result=ini_set(...factoryFirstOwning91());echo "BAD;";}
catch (TypeError $error) {
    echo "E:",(int)($error->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        (int)($payloadWatch->get()===null),";";
    $trace=$error->getTrace();$arg=$trace[0]["args"][0];
    echo "A:",(int)($arg===$payloadWatch->get()),":",$arg->tag,":",
        $trace[0]["args"][1],";";
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
    'config-generator-factory-first-owning-reference-object-typeerror':
        BODY + b'$mode="normal";\n' + CALL,
    'config-generator-factory-first-owning-reference-object-terminal-throw':
        BODY + b'$mode="throw";\n' + CALL,
    'config-generator-factory-first-owning-reference-object-early-throw':
        BODY + b'$mode="early";\n' + CALL,
}

PREFIX = b'B;P;Y0;M:5;W:1;Y1;T:8;'
EXPECTED = {
    'config-generator-factory-first-owning-reference-object-typeerror':
        PREFIX + b'E:1:99:6:1:0;A:1:5:7;U:1:1;R:6:9;',
    'config-generator-factory-first-owning-reference-object-terminal-throw':
        PREFIX + b'S:1:1:99:6:1:1;U:1:1;R:6:9;',
    'config-generator-factory-first-owning-reference-object-early-throw':
        b'B;P;Y0;M:5;W:1;T:early;S:1:1:99:6:1:1;U:1:1;R:6:9;',
}
