"""A copied owning reference yield survives a later local cell overwrite."""

BODY = b'''<?php
class RefOwning81 {public int $tag=4;}
function &refOwningGenerator81() {
    $payload=new RefOwning81();
    $GLOBALS["payloadWatch"]=WeakReference::create($payload);
    echo "Y0;";yield 0=>$payload;
    $payload->tag=5;echo "M:",$payload->tag,";";
    $payload=7;echo "W:",(int)($GLOBALS["payloadWatch"]->get()!==null),";";
    echo "Y1;";yield 1=>$payload;
    ini_set("precision",6);echo "T;";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
}
ini_set("precision",14);$payloadWatch=null;
$gen=refOwningGenerator81();$genWatch=WeakReference::create($gen);
$result=99;$saved=new Exception("reference-owning81");
'''

CALL = b'''echo "B;";
try {$result=ini_set(...$gen);echo "BAD;";}
catch (TypeError $error) {
    echo "E:",(int)($error->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        (int)($payloadWatch->get()===null),";";
    $trace=$error->getTrace();$arg=$trace[0]["args"][0];
    echo "P:",(int)($arg===$payloadWatch->get()),":",$arg->tag,":",
        $trace[0]["args"][1],";";
    unset($arg,$trace,$error);
} catch (Exception $caught) {
    echo "S:",(int)($caught===$saved),":",
        (int)($caught->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        (int)($payloadWatch->get()===null),";";
}
echo "U:",(int)($payloadWatch->get()===null),";";
unset($gen);echo "V:",(int)($genWatch->get()===null),";";
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($caught,$saved,$genWatch,$payloadWatch,$result,$mode);
'''

CASES = {
    'config-generator-reference-owning-object-typeerror':
        BODY + b'$mode="normal";\n' + CALL,
    'config-generator-reference-owning-object-terminal-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;Y0;M:5;W:1;Y1;T;'
EXPECTED = {
    'config-generator-reference-owning-object-typeerror':
        PREFIX + b'E:1:99:6:0:0;P:1:5:7;U:1;V:1;R:6:9;',
    'config-generator-reference-owning-object-terminal-throw':
        PREFIX + b'S:1:1:99:6:0:1;U:1;V:1;R:6:9;',
}
