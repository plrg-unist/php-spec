"""A Generator's copied NULL option reaches weak INI validation after DATA cleanup."""

BODY = b'''<?php
function scalarReviewGenerator71() {
    echo "Y0;";
    $GLOBALS["input"] = 17;
    yield 3 => $GLOBALS["option"];
    echo "Y1;";
    $GLOBALS["option"] = "precision";
    yield 3 => $GLOBALS["value"];
    echo "F;";
    $GLOBALS["call"] = ini_get(...);
    $GLOBALS["value"] = 31;
    ini_set("precision", 19);
}
function scalarReviewHandler71($level, $message) {
    echo "H:",(int)($level===E_DEPRECATED),":",
        (int)($message==='ini_set(): Passing null to parameter #1 ($option) of type string is deprecated'),":",
        (int)($GLOBALS["watch"]->get()===null),":",ini_get("precision"),":",
        $GLOBALS["result"],":",$GLOBALS["option"],":",$GLOBALS["value"],":",
        (int)($GLOBALS["call"]("precision")===ini_get("precision")),":",
        (int)($GLOBALS["input"]===17),";";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
    return true;
}
ini_set("precision", 14);
$option=null;$value=13;$input=scalarReviewGenerator71();
$watch=WeakReference::create($input);
$call=ini_set(...);$keep=$call;$result=99;
$saved=new Exception("scalar-review71");
'''

CALL = b'''set_error_handler("scalarReviewHandler71", E_DEPRECATED);echo "B;";
try {
    $result=$call(...$input);
    echo "R:",(int)($result===false),":",ini_get("precision"),":",
        (int)($watch->get()===null),":",$option,":",$value,":",$call("precision"),";";
} catch (Exception $e) {
    echo "E:",(int)($e===$saved),":",(int)($e->getPrevious()===null),":",
        $result,":",ini_get("precision"),":",(int)($watch->get()===null),":",
        $option,":",$value,":",$call("precision"),";";
} finally {restore_error_handler();}
'''

CASES = {
    'config-generator-scalar-null-option-handler-return':
        BODY + b'$mode="return";\n' + CALL,
    'config-generator-scalar-null-option-handler-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;Y0;Y1;F;H:1:1:1:19:99:precision:31:1:1;'
EXPECTED = {
    'config-generator-scalar-null-option-handler-return':
        PREFIX + b'R:1:19:1:precision:31:19;',
    'config-generator-scalar-null-option-handler-throw':
        PREFIX + b'E:1:1:99:19:1:precision:31:19;',
}
