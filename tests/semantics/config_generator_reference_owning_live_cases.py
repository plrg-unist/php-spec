"""A retained BYREF Generator keeps its final owning cell alive after unpack."""

BODY = b'''<?php
class RefOwningLive83 {public int $tag=4;}
function &refOwningLive83() {
    $option="precision";echo "Y0;";yield 0=>$option;
    $payload=new RefOwningLive83();
    $GLOBALS["payloadWatch"]=WeakReference::create($payload);
    echo "Y1;";yield 1=>$payload;
    $payload->tag=5;echo "M:",$payload->tag,";";
    echo "W:",(int)($GLOBALS["payloadWatch"]->get()!==null),";";
    ini_set("precision",6);echo "T;";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
}
ini_set("precision",14);$payloadWatch=null;
$gen=refOwningLive83();$genWatch=WeakReference::create($gen);
$result=99;$saved=new Exception("reference-owning-live83");
'''

CALL = b'''echo "B;";
try {$result=ini_set(...$gen);echo "BAD;";}
catch (TypeError $error) {
    echo "E:",(int)($error->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        (int)($payloadWatch->get()===null),";";
    $trace=$error->getTrace();$arg=$trace[0]["args"][1];
    echo "P:",$trace[0]["args"][0],":",
        (int)($arg===$payloadWatch->get()),":",$arg->tag,";";
    unset($arg,$trace,$error);
} catch (Exception $caught) {
    echo "S:",(int)($caught===$saved),":",
        (int)($caught->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        (int)($payloadWatch->get()===null),";";
}
echo "U:",(int)($payloadWatch->get()===null),";";
unset($gen);echo "V:",(int)($genWatch->get()===null),":",
    (int)($payloadWatch->get()===null),";";
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($caught,$saved,$genWatch,$payloadWatch,$result,$mode);
'''

CASES = {
    'config-generator-reference-owning-live-object-typeerror':
        BODY + b'$mode="normal";\n' + CALL,
    'config-generator-reference-owning-live-object-terminal-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;Y0;Y1;M:5;W:1;T;'
EXPECTED = {
    'config-generator-reference-owning-live-object-typeerror':
        PREFIX + b'E:1:99:6:0:0;P:precision:1:5;U:0;V:1:1;R:6:9;',
    'config-generator-reference-owning-live-object-terminal-throw':
        PREFIX + b'S:1:1:99:6:0:0;U:0;V:1:1;R:6:9;',
}
