"""CAST death skips a live replacement key after both saved locators retire."""

CASES = [{
    'id': 'request-base-variable-key-shared-reference-cast-release',
    'source': '''<?php
function requestVariableRelease($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "base";
    $replacement = 99;
    $GLOBALS[$name] =& $replacement;
    $name = "key";
    $GLOBALS[$name] =& $replacement;
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$key = false;
$got = 99;
set_error_handler("requestVariableRelease");
$got = $base[$key];
echo "R:", $got === null ? "null" : "other", ";B:", $base, ";K:", $key, ";";
$base = 100;
echo "V:", $key, ";Z;";
''',
    'expected_stdout': '2:String offset cast occurred;R:null;B:99;K:99;V:100;Z;',
    'expected_warnings': [],
    'read_line': 17,
}, {
    'id': 'request-base-variable-key-distinct-reference-cast-release',
    'source': '''<?php
function requestVariablePrior($level, $message, $file, $line) {
    return true;
}
function requestVariableRelease($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "base";
    $replacementBase = 99;
    $GLOBALS[$name] =& $replacementBase;
    $name = "key";
    $replacementKey = 999;
    $GLOBALS[$name] =& $replacementKey;
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$key = true;
$got = 99;
set_error_handler("requestVariablePrior", 2);
set_error_handler("requestVariableRelease");
$got = $base[$key];
echo "R:", $got === null ? "null" : "other", ";B:", $base, ";K:", $key, ";";
$base = 100;
echo "V:", $key, ";Z;";
''',
    'expected_stdout': '2:String offset cast occurred;R:null;B:99;K:999;V:999;Z;',
    'expected_warnings': [],
    'read_line': 22,
}]
