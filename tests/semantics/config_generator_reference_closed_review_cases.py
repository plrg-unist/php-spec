"""A dead local reference cache precedes weak NULL-option callbacks."""

BODY = b'''<?php
function &closedReferenceReviewGenerator73() {
    echo "Y0;";
    $GLOBALS["input"] = 17;
    $option = null;
    yield 3 => $option;
    echo "Y1;";
    $option = "precision";
    $value = 13;
    yield 3 => $value;
    echo "F;";
    $GLOBALS["call"] = ini_get(...);
    $value = 31;
    $GLOBALS["after"] = $value;
    ini_set("precision", 19);
}
function closedReferenceReviewHandler73($level, $message) {
    echo "H:",(int)($level===E_DEPRECATED),":",
        (int)($message==='ini_set(): Passing null to parameter #1 ($option) of type string is deprecated'),":",
        (int)($GLOBALS["watch"]->get()===null),":",ini_get("precision"),":",
        $GLOBALS["result"],":",$GLOBALS["after"],":",
        (int)($GLOBALS["call"]("precision")===ini_get("precision")),":",
        (int)($GLOBALS["input"]===17),";";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
    return true;
}
ini_set("precision", 14);
$input=closedReferenceReviewGenerator73();
$watch=WeakReference::create($input);
$call=ini_set(...);$keep=$call;$result=99;$after=0;
$saved=new Exception("closed-reference-review73");
'''

CALL = b'''set_error_handler("closedReferenceReviewHandler73", E_DEPRECATED);echo "B;";
try {
    $result=$call(...$input);
    echo "R:",(int)($result===false),":",ini_get("precision"),":",
        (int)($watch->get()===null),":",$after,":",$call("precision"),";";
} catch (Exception $e) {
    echo "E:",(int)($e===$saved),":",(int)($e->getPrevious()===null),":",
        $result,":",ini_get("precision"),":",(int)($watch->get()===null),":",
        $after,":",$call("precision"),";";
} finally {restore_error_handler();}
'''

CASES = {
    'config-generator-reference-closed-null-handler-return':
        BODY + b'$mode="return";\n' + CALL,
    'config-generator-reference-closed-null-handler-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;Y0;Y1;F;H:1:1:1:19:99:31:1:1;'
EXPECTED = {
    'config-generator-reference-closed-null-handler-return':
        PREFIX + b'R:1:19:1:31:19;',
    'config-generator-reference-closed-null-handler-throw':
        PREFIX + b'E:1:1:99:19:1:31:19;',
}
