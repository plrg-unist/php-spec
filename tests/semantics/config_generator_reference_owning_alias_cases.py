"""An outside alias keeps the final BYREF Generator cell after Gen retirement."""

BODY = b'''<?php
class RefOwningAlias84 {public int $tag=4;}
function &refOwningAlias84() {
    global $slot;
    $option="precision";echo "Y0;";yield 0=>$option;
    echo "Y1;";yield 1=>$slot;
    $slot->tag=5;echo "M:",$slot->tag,";";
    echo "W:",(int)($GLOBALS["payloadWatch"]->get()!==null),";";
    ini_set("precision",6);echo "T;";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
}
ini_set("precision",14);
$slot=new RefOwningAlias84();$alias =& $slot;
$payloadWatch=WeakReference::create($slot);
$gen=refOwningAlias84();$genWatch=WeakReference::create($gen);
$result=99;$saved=new Exception("reference-owning-alias84");
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
echo "L:",(int)($payloadWatch->get()!==null),":",$alias->tag,";";
unset($gen);echo "G:",(int)($genWatch->get()===null),":",
    (int)($payloadWatch->get()===null),";";
$alias->tag=8;echo "A:",$slot->tag,":",$alias->tag,";";
unset($slot,$alias);echo "U:",(int)($payloadWatch->get()===null),";";
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($caught,$saved,$genWatch,$payloadWatch,$result,$mode);
'''

CASES = {
    'config-generator-reference-owning-alias-object-typeerror':
        BODY + b'$mode="normal";\n' + CALL,
    'config-generator-reference-owning-alias-object-terminal-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;Y0;Y1;M:5;W:1;T;'
EXPECTED = {
    'config-generator-reference-owning-alias-object-typeerror':
        PREFIX + b'E:1:99:6:0:0;P:precision:1:5;L:1:5;G:1:0;A:8:8;U:1;R:6:9;',
    'config-generator-reference-owning-alias-object-terminal-throw':
        PREFIX + b'S:1:1:99:6:0:0;L:1:5;G:1:0;A:8:8;U:1;R:6:9;',
}
