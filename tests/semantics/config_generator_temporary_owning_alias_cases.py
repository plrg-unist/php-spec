"""A temporary BYREF Generator leaves two aliases of its final owning cell."""

BODY = b'''<?php
class TempOwningAlias86 {public int $tag=4;}
function &tempOwningAlias86() {
    $option="precision";echo "Y0;";yield 0=>$option;
    $payload=new TempOwningAlias86();
    $GLOBALS["payloadWatch"]=WeakReference::create($payload);
    $GLOBALS["slot"] =& $payload;
    $GLOBALS["alias"] =& $payload;
    echo "Y1;";yield 1=>$payload;
    $payload->tag=5;
    echo "M:",$GLOBALS["slot"]->tag,":",$GLOBALS["alias"]->tag,";";
    ini_set("precision",6);echo "T;";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
}
ini_set("precision",14);$slot=null;$alias=null;$payloadWatch=null;
$result=99;$saved=new Exception("temporary-owning-alias86");
'''

CALL = b'''echo "B;";
try {$result=ini_set(...tempOwningAlias86());echo "BAD;";}
catch (TypeError $error) {
    echo "E:",(int)($error->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($payloadWatch->get()!==null),":",
        $slot->tag,":",$alias->tag,";";
    $trace=$error->getTrace();$arg=$trace[0]["args"][1];
    echo "P:",$trace[0]["args"][0],":",
        (int)($arg===$payloadWatch->get()),":",$arg->tag,";";
    unset($arg,$trace,$error);
} catch (Exception $caught) {
    echo "S:",(int)($caught===$saved),":",
        (int)($caught->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($payloadWatch->get()!==null),":",
        $slot->tag,":",$alias->tag,";";
}
echo "A:",(int)($payloadWatch->get()!==null),";";
unset($slot);
echo "L:",(int)($payloadWatch->get()!==null),":",$alias->tag,";";
unset($alias);
echo "U:",(int)($payloadWatch->get()===null),";";
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($caught,$saved,$payloadWatch,$result,$mode);
'''

CASES = {
    'config-generator-temporary-owning-alias-object-typeerror':
        BODY + b'$mode="normal";\n' + CALL,
    'config-generator-temporary-owning-alias-object-terminal-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;Y0;Y1;M:5:5;T;'
EXPECTED = {
    'config-generator-temporary-owning-alias-object-typeerror':
        PREFIX + b'E:1:99:6:1:5:5;P:precision:1:5;A:1;L:1:5;U:1;R:6:9;',
    'config-generator-temporary-owning-alias-object-terminal-throw':
        PREFIX + b'S:1:1:99:6:1:5:5;A:1;L:1:5;U:1;R:6:9;',
}
