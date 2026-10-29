"""A surviving scalar alias may become an array after Generator DATA dies."""

BODY = b'''<?php
function &outsideAliasReviewGenerator74() {
    global $input,$call,$value;
    echo "Y0;";
    $input = 17;
    $option = null;
    yield 3 => $option;
    echo "Y1;";
    $option = "precision";
    yield 3 => $value;
    echo "F;";
    $call = ini_get(...);
    $value = 31;
    ini_set("precision", 19);
}
function outsideAliasReviewHandler74($level, $message) {
    echo "H:",(int)($level===E_DEPRECATED),":",
        (int)($message==='ini_set(): Passing null to parameter #1 ($option) of type string is deprecated'),":",
        (int)($GLOBALS["watch"]->get()===null),":",ini_get("precision"),":",
        $GLOBALS["result"],":",$GLOBALS["value"],":",
        (int)($GLOBALS["alias"]===$GLOBALS["value"]),";";
    $GLOBALS["alias"] = [41];
    echo "M:",(int)($GLOBALS["value"]===[41]),":",
        (int)($GLOBALS["alias"]===$GLOBALS["value"]),";";
    if ($GLOBALS["mode"]==="throw") {throw $GLOBALS["saved"];}
    return true;
}
ini_set("precision", 14);
$value=13;$alias=&$value;$input=outsideAliasReviewGenerator74();
$watch=WeakReference::create($input);
$call=ini_set(...);$keep=$call;$result=99;
$saved=new Exception("outside-alias-review74");
'''

CALL = b'''set_error_handler("outsideAliasReviewHandler74", E_DEPRECATED);echo "B;";
try {
    $result=$call(...$input);
    echo "R:",(int)($result===false),":",ini_get("precision"),":",
        (int)($watch->get()===null),":",$value[0],":",
        (int)($alias===$value),":",$call("precision"),";";
} catch (Exception $e) {
    echo "E:",(int)($e===$saved),":",(int)($e->getPrevious()===null),":",
        $result,":",ini_get("precision"),":",(int)($watch->get()===null),":",
        $value[0],":",(int)($alias===$value),":",$call("precision"),";";
} finally {restore_error_handler();}
'''

CASES = {
    'config-generator-reference-outside-alias-null-handler-return':
        BODY + b'$mode="return";\n' + CALL,
    'config-generator-reference-outside-alias-null-handler-throw':
        BODY + b'$mode="throw";\n' + CALL,
}

PREFIX = b'B;Y0;Y1;F;H:1:1:1:19:99:31:1;M:1:1;'
EXPECTED = {
    'config-generator-reference-outside-alias-null-handler-return':
        PREFIX + b'R:1:19:1:41:1:19;',
    'config-generator-reference-outside-alias-null-handler-throw':
        PREFIX + b'E:1:1:99:19:1:41:1:19;',
}
