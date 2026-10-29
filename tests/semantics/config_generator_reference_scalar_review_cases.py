"""By-reference Generator scalar cells are copied before later resumes."""

BODY = b'''<?php
function &referenceScalarGenerator72() {
    global $option, $value, $input, $call, $abort, $saved;
    echo "Y0;";
    $input = 17;
    $call = ini_get(...);
    yield 3 => $option;
    echo "Y1;";
    $option = "serialize_precision";
    $value = 17;
    yield 3 => $value;
    echo "F;";
    $value = 31;
    ini_set("precision", 7);
    if ($abort) {throw $saved;}
}
ini_set("precision", 14);
$option="precision";$value=13;$input=referenceScalarGenerator72();
$hold=$input;$watch=WeakReference::create($input);
$call=ini_set(...);$keep=$call;$result=99;
$saved=new Exception("reference-scalar72");
'''

CALL = b'''echo "B;";
try {
    $result=$call(...$input);
    echo "A:",$result,":",ini_get("precision"),":",$option,":",$value,":",
        (int)($watch->get()===$hold),":",$call("precision"),";";
} catch (Exception $e) {
    echo "E:",(int)($e===$saved),":",(int)($e->getPrevious()===null),":",
        $result,":",ini_get("precision"),":",$option,":",$value,":",
        (int)($watch->get()===$hold),":",$call("precision"),";";
}
unset($hold);
echo "R:",(int)($watch->get()===null),";";
'''

CASES = {
    'config-generator-reference-scalar-copies-before-later-cell-writes':
        BODY + b'$abort=false;\n' + CALL,
    'config-generator-reference-scalar-saved-terminal-throw':
        BODY + b'$abort=true;\n' + CALL,
}

PREFIX = b'B;Y0;Y1;F;'
EXPECTED = {
    'config-generator-reference-scalar-copies-before-later-cell-writes':
        PREFIX + b'A:7:17:serialize_precision:31:1:17;R:1;',
    'config-generator-reference-scalar-saved-terminal-throw':
        PREFIX + b'E:1:1:99:7:serialize_precision:31:1:7;R:1;',
}
