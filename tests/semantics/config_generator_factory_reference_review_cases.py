"""A BYVAL factory's weak observer sees BYREF Generator death before handlers."""

BODY = b'''<?php
function &factoryReferenceReviewBody76() {
    global $call;
    echo "Y0;";
    $option = null;
    yield 0 => $option;
    echo "Y1;";
    $option = "precision";
    $value = 13;
    yield 1 => $value;
    $value = 31;
    $call = ini_get(...);
    ini_set("precision", 19);
    echo "F;";
}
function factoryReferenceReview76() {
    $gen=factoryReferenceReviewBody76();
    $GLOBALS["watch"]=WeakReference::create($gen);
    echo "P;";
    return $gen;
}
function factoryReferenceReviewHandler76($level, $message) {
    echo "H:",(int)($level===E_DEPRECATED),":",
        (int)($message==='ini_set(): Passing null to parameter #1 ($option) of type string is deprecated'),":",
        (int)($GLOBALS["watch"]->get()===null),":",
        ini_get("precision"),":",$GLOBALS["result"],";";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
    return true;
}
ini_set("precision", 14);$watch=null;
$call=ini_set(...);$keep=$call;$result=99;
$saved=new Exception("factory-reference-review76");
'''

CALL = b'''set_error_handler("factoryReferenceReviewHandler76", E_DEPRECATED);echo "B;";
try {
    $result=$call(...factoryReferenceReview76());
    echo "R:",(int)($result===false),":",ini_get("precision"),":",
        (int)($watch->get()===null),":",$call("precision"),";";
} catch (Exception $e) {
    echo "E:",(int)($e===$saved),":",(int)($e->getPrevious()===null),":",
        $result,":",ini_get("precision"),":",
        (int)($watch->get()===null),":",$call("precision"),";";
} finally {restore_error_handler();}
echo "Q:",ini_set("precision", 9),":",ini_get("precision"),";";
unset($watch,$e,$saved,$result,$call,$keep);
'''

CASES = {
    'config-generator-factory-reference-null-handler-return':
        BODY + b'$mode="return";\n' + CALL,
    'config-generator-factory-reference-null-handler-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;P;Y0;Y1;F;H:1:1:1:19:99;'
EXPECTED = {
    'config-generator-factory-reference-null-handler-return':
        PREFIX + b'R:1:19:1:19;Q:19:9;',
    'config-generator-factory-reference-null-handler-throw':
        PREFIX + b'E:1:1:99:19:1:19;Q:19:9;',
}
