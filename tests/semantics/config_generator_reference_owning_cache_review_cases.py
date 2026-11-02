"""A final copied ARRAY keeps its old value after the shared cache cell changes."""

BODY = b'''<?php
function &refOwningCacheReview82() {
    global $slot;
    $slot="precision";echo "Y0;";yield 0=>$slot;
    $seed=13;$slot=[$seed];echo "Y1;";yield 1=>$slot;
    $slot[0]=31;echo "C:",$slot[0],";";
    $slot=9;ini_set("precision",6);echo "T;";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
}
ini_set("precision",14);$slot=null;$alias=&$slot;
$gen=refOwningCacheReview82();$genWatch=WeakReference::create($gen);
$result=99;$saved=new Exception("reference-owning-cache-review82");
'''

CALL = b'''echo "B;";
try {$result=ini_set(...$gen);echo "BAD;";}
catch (TypeError $error) {
    echo "E:",(int)($error->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",$alias,";";
    $trace=$error->getTrace();
    echo "A:",$trace[0]["args"][0],":",$trace[0]["args"][1][0],";";
    unset($trace,$error);
} catch (Exception $caught) {
    echo "S:",(int)($caught===$saved),":",
        (int)($caught->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",$alias,";";
}
unset($gen);echo "V:",(int)($genWatch->get()===null),":",$alias,";";
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($caught,$saved,$genWatch,$result,$mode,$slot,$alias);
'''

CASES = {
    'config-generator-reference-owning-cache-array-cow-typeerror':
        BODY + b'$mode="normal";\n' + CALL,
    'config-generator-reference-owning-cache-array-cow-terminal-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;Y0;Y1;C:31;T;'
EXPECTED = {
    'config-generator-reference-owning-cache-array-cow-typeerror':
        PREFIX + b'E:1:99:6:0:9;A:precision:13;V:1:9;R:6:9;',
    'config-generator-reference-owning-cache-array-cow-terminal-throw':
        PREFIX + b'S:1:1:99:6:0:9;V:1:9;R:6:9;',
}
