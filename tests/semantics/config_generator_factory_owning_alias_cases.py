"""A BYVAL factory returns a BYREF Generator with outside aliases of its cell."""

BODY = b'''<?php
class FactoryOwningAlias88 {public int $tag=4;}
function &factoryOwningAliasBody88() {
    $option="precision";echo "Y0;";yield 0=>$option;
    $payload=new FactoryOwningAlias88();
    $GLOBALS["payloadWatch"]=WeakReference::create($payload);
    $GLOBALS["slot"] =& $payload;
    $GLOBALS["alias"] =& $payload;
    echo "Y1;";yield 1=>$payload;
    $payload->tag=5;
    echo "M:",$GLOBALS["slot"]->tag,":",$GLOBALS["alias"]->tag,";";
    ini_set("precision",6);echo "T;";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
}
function factoryOwningAlias88() {
    $gen=factoryOwningAliasBody88();
    $GLOBALS["genWatch"]=WeakReference::create($gen);
    echo "P;";
    return $gen;
}
ini_set("precision",14);$slot=null;$alias=null;
$genWatch=null;$payloadWatch=null;$result=99;
$saved=new Exception("factory-owning-alias88");
'''

CALL = b'''echo "B;";
try {$result=ini_set(...factoryOwningAlias88());echo "BAD;";}
catch (TypeError $error) {
    echo "E:",(int)($error->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        (int)($payloadWatch->get()!==null),":",$slot->tag,":",$alias->tag,";";
    $trace=$error->getTrace();$arg=$trace[0]["args"][1];
    echo "A:",$trace[0]["args"][0],":",
        (int)($arg===$payloadWatch->get()),":",$arg->tag,";";
    unset($arg,$trace,$error);
} catch (Exception $caught) {
    echo "S:",(int)($caught===$saved),":",
        (int)($caught->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        (int)($payloadWatch->get()!==null),":",$slot->tag,":",$alias->tag,";";
}
echo "W:",(int)($genWatch->get()===null),";";
unset($slot);
echo "L:",(int)($payloadWatch->get()!==null),":",$alias->tag,";";
unset($alias);
echo "U:",(int)($payloadWatch->get()===null),";";
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($caught,$saved,$genWatch,$payloadWatch,$result,$mode);
'''

CASES = {
    'config-generator-factory-owning-alias-object-typeerror':
        BODY + b'$mode="normal";\n' + CALL,
    'config-generator-factory-owning-alias-object-terminal-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;P;Y0;Y1;M:5:5;T;'
EXPECTED = {
    'config-generator-factory-owning-alias-object-typeerror':
        PREFIX + b'E:1:99:6:1:1:5:5;A:precision:1:5;W:1;L:1:5;U:1;R:6:9;',
    'config-generator-factory-owning-alias-object-terminal-throw':
        PREFIX + b'S:1:1:99:6:1:1:5:5;W:1;L:1:5;U:1;R:6:9;',
}
