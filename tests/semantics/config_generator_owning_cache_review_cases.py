"""A temporary Generator retains its final copied array until storage release."""

BODY = b'''<?php
function owningCacheReviewBody79() {
    $seed=13;$row=[$seed];
    echo "Y0;";yield 0=>"precision";
    echo "Y1;";yield 1=>$row;
    $row[0]=31;echo "M:",$row[0],";";unset($row);
    ini_set("precision",6);echo "T;";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
}
function owningCacheReviewFactory79() {
    $gen=owningCacheReviewBody79();
    $GLOBALS["genWatch"]=WeakReference::create($gen);
    echo "P;";return $gen;
}
ini_set("precision",14);$genWatch=null;$result=99;
$saved=new Exception("owning-cache-review79");
'''

CALL = b'''echo "B;";
try {$result=ini_set(...owningCacheReviewFactory79());echo "BAD;";}
catch (TypeError $error) {
    echo "E:",(int)($error->getPrevious()===null),":",$result,":",
        ini_get("precision"),":",(int)($genWatch->get()===null),";";
    $trace=$error->getTrace();
    echo "A:",$trace[0]["args"][0],":",$trace[0]["args"][1][0],";";
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
    'config-generator-owning-cache-array-typeerror':
        BODY + b'$mode="normal";\n' + CALL,
    'config-generator-owning-cache-array-terminal-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;P;Y0;Y1;M:31;T;'
EXPECTED = {
    'config-generator-owning-cache-array-typeerror':
        PREFIX + b'E:1:99:6:1;A:precision:13;R:6:9;',
    'config-generator-owning-cache-array-terminal-throw':
        PREFIX + b'S:1:1:99:6:1;R:6:9;',
}
