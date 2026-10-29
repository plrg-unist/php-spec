"""Temporary BYREF sends retain copied NULL/scalar arguments through handlers."""

BODY = b'''<?php
function &temporaryReferenceReview75() {
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
function temporaryReferenceReviewHandler75($level, $message) {
    echo "H:",(int)($level===E_DEPRECATED),":",
        (int)($message==='ini_set(): Passing null to parameter #1 ($option) of type string is deprecated'),":",
        ini_get("precision"),":",$GLOBALS["result"],";";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
    return true;
}
ini_set("precision", 14);
$call=ini_set(...);$keep=$call;$result=99;
$saved=new Exception("temporary-reference-review75");
'''

CALL = b'''set_error_handler("temporaryReferenceReviewHandler75", E_DEPRECATED);echo "B;";
try {
    $result=$call(...temporaryReferenceReview75());
    echo "R:",(int)($result===false),":",ini_get("precision"),":",
        $call("precision"),";";
} catch (Exception $e) {
    echo "E:",(int)($e===$saved),":",(int)($e->getPrevious()===null),":",
        $result,":",ini_get("precision"),":",$call("precision"),";";
} finally {restore_error_handler();}
echo "Q:",ini_set("precision", 9),":",ini_get("precision"),";";
unset($e,$saved,$result,$call,$keep);
'''

CASES = {
    'config-generator-temporary-reference-null-handler-return':
        BODY + b'$mode="return";\n' + CALL,
    'config-generator-temporary-reference-null-handler-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;Y0;Y1;F;H:1:1:19:99;'
EXPECTED = {
    'config-generator-temporary-reference-null-handler-return':
        PREFIX + b'R:1:19:19;Q:19:9;',
    'config-generator-temporary-reference-null-handler-throw':
        PREFIX + b'E:1:1:99:19:19;Q:19:9;',
}
