"""A factory temporary retires before observing a copied dynamic array option."""

BODY = b'''<?php
function owningTemporaryReviewBody78() {
    $seed=13;$row=[$seed];
    echo "Y0;";yield 0=>$row;
    $row[0]=31;echo "M:",$row[0],";";
    echo "Y1;";yield 1=>7;
    ini_set("precision",6);echo "F;";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
}
function owningTemporaryReviewFactory78() {
    $gen=owningTemporaryReviewBody78();
    $GLOBALS["genWatch"]=WeakReference::create($gen);
    echo "P;";
    return $gen;
}
ini_set("precision",14);$genWatch=null;$result=99;
$saved=new Exception("owning-temporary-review78");
'''

CALL = b'''echo "B;";
try {$result=ini_set(...owningTemporaryReviewFactory78());echo "BAD;";}
catch (TypeError $error) {
    echo "E:",(int)($error->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),";";
    $trace=$error->getTrace();
    echo "T:",$trace[0]["args"][0][0],":",$trace[0]["args"][1],";";
    unset($trace,$error);
} catch (Exception $caught) {
    echo "S:",(int)($caught===$saved),":",
        (int)($caught->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),";";
}
echo "R:",ini_set("precision",9),":",ini_get("precision"),";";
unset($caught,$saved,$genWatch,$result,$mode);
'''

CASES = {
    'config-generator-owning-temporary-array-cow-typeerror':
        BODY + b'$mode="normal";\n' + CALL,
    'config-generator-owning-temporary-array-cow-terminal-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;P;Y0;M:31;Y1;F;'
EXPECTED = {
    'config-generator-owning-temporary-array-cow-typeerror':
        PREFIX + b'E:1:99:6:1;T:13:7;R:6:9;',
    'config-generator-owning-temporary-array-cow-terminal-throw':
        PREFIX + b'S:1:1:99:6:1;R:6:9;',
}
