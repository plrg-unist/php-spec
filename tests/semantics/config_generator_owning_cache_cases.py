"""A temporary Generator retains a quiet final object across cached-value release."""

BODY = b'''<?php
class OwningCacheValue79 {public int $tag=4;}
function owningCacheBody79() {
    echo "Y0;";yield 0=>"precision";
    $payload=new OwningCacheValue79();
    $GLOBALS["payloadWatch"]=WeakReference::create($payload);
    echo "Y1;";yield 1=>$payload;
    $payload->tag=5;echo "M:",$payload->tag,";";unset($payload);
    ini_set("precision",6);echo "T;";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
}
function owningCacheFactory79() {
    $gen=owningCacheBody79();
    $GLOBALS["genWatch"]=WeakReference::create($gen);
    echo "P;";return $gen;
}
ini_set("precision",14);$genWatch=null;$payloadWatch=null;$result=99;
$saved=new Exception("owning-cache79");
'''

CALL = b'''echo "B;";
try {$result=ini_set(...owningCacheFactory79());echo "BAD;";}
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
echo "U:",(int)($payloadWatch->get()===null),";";
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($caught,$saved,$genWatch,$payloadWatch,$result,$mode);
'''

CASES = {
    'config-generator-owning-cache-object-typeerror':
        BODY + b'$mode="normal";\n' + CALL,
    'config-generator-owning-cache-object-terminal-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;P;Y0;Y1;M:5;T;'
EXPECTED = {
    'config-generator-owning-cache-object-typeerror':
        PREFIX + b'E:1:99:6:1:0;A:precision:1:5;U:1;R:6:9;',
    'config-generator-owning-cache-object-terminal-throw':
        PREFIX + b'S:1:1:99:6:1:1;U:1;R:6:9;',
}
