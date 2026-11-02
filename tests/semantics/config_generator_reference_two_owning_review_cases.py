"""A retained BYREF Generator copies one object from two ordinary cells."""

BODY = b'''<?php
class SharedRetainedRefReview93 {public int $tag=4;}
function &twoOwningRefsReview93() {
    $first=new SharedRetainedRefReview93();
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
ini_set("precision",14);$payloadWatch=null;
$gen=twoOwningRefsReview93();$genWatch=WeakReference::create($gen);
$result=99;$saved=new Exception("reference-two-owning-review93");
'''

CALL = b'''echo "B;";
try {$result=ini_set(...$gen);echo "BAD;";}
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
unset($gen);echo "V:",(int)($genWatch->get()===null),":",
    (int)($payloadWatch->get()===null),";";
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($caught,$saved,$genWatch,$payloadWatch,$result,$mode);
'''

CASES = {
    'config-generator-reference-two-owning-shared-typeerror':
        BODY + b'$mode="normal";\n' + CALL,
    'config-generator-reference-two-owning-shared-terminal-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;Y0;M0:5;W0:1;Y1;M1:8;W1:1;T;'
EXPECTED = {
    'config-generator-reference-two-owning-shared-typeerror':
        PREFIX + b'E:1:99:6:0:0;A:1:1:8:8;U:0:0;V:1:1;R:6:9;',
    'config-generator-reference-two-owning-shared-terminal-throw':
        PREFIX + b'S:1:1:99:6:0:0;U:0:0;V:1:1;R:6:9;',
}
