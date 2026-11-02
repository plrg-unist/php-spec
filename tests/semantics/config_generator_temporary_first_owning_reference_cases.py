"""A temporary BYREF Generator copies an owning first cell before a scalar last cell."""

BODY = b'''<?php
class TempFirstOwning89 {public int $tag=4;}
function &tempFirstOwning89() {
    $payload=new TempFirstOwning89();
    $GLOBALS["payloadWatch"]=WeakReference::create($payload);
    echo "Y0;";yield 0=>$payload;
    $payload->tag=5;echo "M:",$payload->tag,";";
    $payload=9;echo "W:",(int)($GLOBALS["payloadWatch"]->get()!==null),";";
    $value=7;echo "Y1;";yield 1=>$value;
    $value=8;ini_set("precision",6);echo "T:",$value,";";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
}
ini_set("precision",14);$payloadWatch=null;
$result=99;$saved=new Exception("temporary-first-owning89");
'''

EARLY_BODY = BODY.replace(
    b'    $value=7;echo "Y1;";yield 1=>$value;\n',
    b'    if ($GLOBALS["mode"]==="early") {ini_set("precision",6);echo "T:early;";throw $GLOBALS["saved"];}\n'
    b'    $value=7;echo "Y1;";yield 1=>$value;\n')
assert EARLY_BODY != BODY

CALL = b'''echo "B;";
try {$result=ini_set(...tempFirstOwning89());echo "BAD;";}
catch (TypeError $error) {
    echo "E:",(int)($error->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($payloadWatch->get()===null),";";
    $trace=$error->getTrace();$arg=$trace[0]["args"][0];
    echo "A:",(int)($arg===$payloadWatch->get()),":",$arg->tag,":",
        $trace[0]["args"][1],";";
    unset($arg,$trace,$error);
} catch (Exception $caught) {
    echo "S:",(int)($caught===$saved),":",
        (int)($caught->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($payloadWatch->get()===null),";";
}
echo "U:",(int)($payloadWatch->get()===null),";";
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($caught,$saved,$payloadWatch,$result,$mode);
'''

CASES = {
    'config-generator-temporary-first-owning-reference-object-typeerror':
        BODY + b'$mode="normal";\n' + CALL,
    'config-generator-temporary-first-owning-reference-object-terminal-throw':
        BODY + b'$mode="throw";\n' + CALL,
    'config-generator-temporary-first-owning-reference-object-early-throw':
        EARLY_BODY + b'$mode="early";\n' + CALL,
}

PREFIX = b'B;Y0;M:5;W:1;Y1;T:8;'
EXPECTED = {
    'config-generator-temporary-first-owning-reference-object-typeerror':
        PREFIX + b'E:1:99:6:0;A:1:5:7;U:1;R:6:9;',
    'config-generator-temporary-first-owning-reference-object-terminal-throw':
        PREFIX + b'S:1:1:99:6:1;U:1;R:6:9;',
    'config-generator-temporary-first-owning-reference-object-early-throw':
        b'B;Y0;M:5;W:1;T:early;S:1:1:99:6:1;U:1;R:6:9;',
}
