"""A retained direct-CV BYREF Generator copies two owning local cells."""

BODY = b'''<?php
class FirstRef93 {public int $tag=4;}
class LastRef93 {public int $tag=7;}
function &refTwoBody93() {
    $first=new FirstRef93();
    $GLOBALS["firstWatch"]=WeakReference::create($first);
    echo "Y0;";yield 0=>$first;
    $first->tag=5;echo "M0:",$first->tag,";";
    $first=9;echo "W0:",(int)($GLOBALS["firstWatch"]->get()!==null),";";
    $last=new LastRef93();
    $GLOBALS["lastWatch"]=WeakReference::create($last);
    echo "Y1;";yield 1=>$last;
    $last->tag=8;echo "M1:",$last->tag,";";
    echo "W1:",(int)($GLOBALS["lastWatch"]->get()!==null),";";
    ini_set("precision",6);echo "T;";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
}
ini_set("precision",14);$gen=refTwoBody93();
$genWatch=WeakReference::create($gen);$firstWatch=null;$lastWatch=null;
$result=99;$saved=new Exception("reference-two-owning93");
'''

CALL = b'''echo "B;";
try {$result=ini_set(...$gen);echo "BAD;";}
catch (TypeError $error) {
    echo "E:",(int)($error->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        (int)($firstWatch->get()===null),":",
        (int)($lastWatch->get()===null),";";
    $trace=$error->getTrace();
    $firstArg=$trace[0]["args"][0];$lastArg=$trace[0]["args"][1];
    echo "A:",(int)($firstArg===$firstWatch->get()),":",$firstArg->tag,":",
        (int)($lastArg===$lastWatch->get()),":",$lastArg->tag,";";
    unset($firstArg,$lastArg,$trace,$error);
} catch (Exception $caught) {
    echo "S:",(int)($caught===$saved),":",
        (int)($caught->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",
        (int)($firstWatch->get()===null),":",
        (int)($lastWatch->get()===null),";";
}
echo "U:",(int)($genWatch->get()===null),":",
    (int)($firstWatch->get()===null),":",
    (int)($lastWatch->get()===null),";";
unset($gen);
echo "V:",(int)($genWatch->get()===null),":",
    (int)($firstWatch->get()===null),":",
    (int)($lastWatch->get()===null),";";
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($caught,$saved,$genWatch,$firstWatch,$lastWatch,$result,$mode);
'''

CASES = {
    'config-generator-reference-two-owning-distinct-typeerror':
        BODY + b'$mode="normal";\n' + CALL,
    'config-generator-reference-two-owning-distinct-terminal-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;Y0;M0:5;W0:1;Y1;M1:8;W1:1;T;'
EXPECTED = {
    'config-generator-reference-two-owning-distinct-typeerror':
        PREFIX + b'E:1:99:6:0:0:0;A:1:5:1:8;U:0:1:0;V:1:1:1;R:6:9;',
    'config-generator-reference-two-owning-distinct-terminal-throw':
        PREFIX + b'S:1:1:99:6:0:1:0;U:0:1:0;V:1:1:1;R:6:9;',
}
