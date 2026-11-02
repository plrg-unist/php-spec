"""A copied ARRAY snapshot differs from a later shared reference-cell value."""

BODY = b'''<?php
function &refOwningReviewGenerator81() {
    global $slot;
    echo "Y0;";yield 0=>$slot;
    $slot[0]=31;echo "C:",$slot[0],";";
    $slot=7;echo "Y1;";yield 1=>$slot;
    $slot=9;ini_set("precision",6);echo "T;";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
}
ini_set("precision",14);$seed=13;$slot=[$seed];$alias=&$slot;
$gen=refOwningReviewGenerator81();$genWatch=WeakReference::create($gen);
$result=99;$saved=new Exception("reference-owning-review81");
'''

CALL = b'''echo "B;";
try {$result=ini_set(...$gen);echo "BAD;";}
catch (TypeError $error) {
    echo "E:",(int)($error->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",$alias,";";
    $trace=$error->getTrace();
    echo "A:",$trace[0]["args"][0][0],":",$trace[0]["args"][1],";";
    unset($trace,$error);
} catch (Exception $caught) {
    echo "S:",(int)($caught===$saved),":",
        (int)($caught->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),":",$alias,";";
}
unset($gen);echo "V:",(int)($genWatch->get()===null),":",$alias,";";
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($caught,$saved,$genWatch,$result,$mode,$slot,$alias,$seed);
'''

CASES = {
    'config-generator-reference-owning-array-cow-typeerror':
        BODY + b'$mode="normal";\n' + CALL,
    'config-generator-reference-owning-array-cow-terminal-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;Y0;C:31;Y1;T;'
EXPECTED = {
    'config-generator-reference-owning-array-cow-typeerror':
        PREFIX + b'E:1:99:6:0:9;A:13:7;V:1:9;R:6:9;',
    'config-generator-reference-owning-array-cow-terminal-throw':
        PREFIX + b'S:1:1:99:6:0:9;V:1:9;R:6:9;',
}
