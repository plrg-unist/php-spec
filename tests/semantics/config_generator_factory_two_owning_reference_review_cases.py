"""A BYVAL factory returns a BYREF Generator copying one object twice."""

BODY = b'''<?php
class SharedFactoryRefReview92 {public int $tag=4;}
function &factoryTwoBodyReview92() {
    $first=new SharedFactoryRefReview92();
    $GLOBALS["payloadWatch"]=WeakReference::create($first);
    echo "Y0;";yield 0=>$first;
    $first->tag=5;echo "M0:",$first->tag,";";
    $last=$first;$first=9;
    echo "W0:",(int)($GLOBALS["payloadWatch"]->get()!==null),";";
    echo "Y1;";yield 1=>$last;
    $last->tag=8;echo "M1:",$last->tag,";";
    echo "W1:",(int)($GLOBALS["payloadWatch"]->get()!==null),";";
    ini_set("precision",6);echo "T;";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
}
function factoryTwoOwningReview92() {
    $gen=factoryTwoBodyReview92();
    $GLOBALS["genWatch"]=WeakReference::create($gen);
    echo "P;";
    return $gen;
}
ini_set("precision",14);$genWatch=null;$payloadWatch=null;
$result=99;$saved=new Exception("factory-two-owning-review92");
'''

CALL = b'''echo "B;";
try {$result=ini_set(...factoryTwoOwningReview92());echo "BAD;";}
catch (TypeError $error) {
    echo "E:",(int)($error->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        (int)($payloadWatch->get()===null),";";
    $trace=$error->getTrace();
    $firstArg=$trace[0]["args"][0];$lastArg=$trace[0]["args"][1];
    echo "A:",(int)($firstArg===$lastArg),":",
        (int)($firstArg===$payloadWatch->get()),":",
        $firstArg->tag,":",$lastArg->tag,";";
    unset($firstArg,$lastArg,$trace,$error);
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
    'config-generator-factory-two-owning-reference-shared-typeerror':
        BODY + b'$mode="normal";\n' + CALL,
    'config-generator-factory-two-owning-reference-shared-terminal-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;P;Y0;M0:5;W0:1;Y1;M1:8;W1:1;T;'
EXPECTED = {
    'config-generator-factory-two-owning-reference-shared-typeerror':
        PREFIX + b'E:1:99:6:1:0;A:1:1:8:8;U:1:1;R:6:9;',
    'config-generator-factory-two-owning-reference-shared-terminal-throw':
        PREFIX + b'S:1:1:99:6:1:1;U:1:1;R:6:9;',
}
