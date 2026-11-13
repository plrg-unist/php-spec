"""Register a different REQUEST callback header with the selected abc bytes."""

CASES = [{
    'id': 'undefined-request-base-request-handler-release-before-cast',
    'source': '''<?php
function requestReleasePrior($level, $message, $file, $line) {
    return true;
}
function abc($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    if ($message === 'Undefined variable $key') {
        $name = "base";
        $replacement = 99;
        $GLOBALS[$name] =& $replacement;
        $name = "key";
        $GLOBALS[$name] = "not-an-offset";
        $name = "keeper";
        unset($GLOBALS[$name]);
    }
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$keeper = $base;
$bystander = $left . $right;
$got = 99;
$handler = $left . $right;
set_error_handler("requestReleasePrior", 2);
set_error_handler($handler);
unset($handler);
$got = $base[$key];
echo "R:", $got === null ? "null" : "other", ";B:", $base, ";K:", $key, ";S:", isset($keeper) ? "live" : "gone", ";V:", $bystander, ";Z;";
''',
    'expected_stdout': '2:Undefined variable $key;R:null;B:99;K:not-an-offset;S:gone;V:abc;Z;',
    'expected_warnings': [],
    'read_line': 28,
}, {
    'id': 'undefined-request-base-request-handler-release-after-cast',
    'source': '''<?php
function abc($level, $message, $file, $line) {
    return true;
}
function requestReleaseCast($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    if ($message === 'Undefined variable $key') {
        $name = "base";
        $replacement = 99;
        $GLOBALS[$name] =& $replacement;
        $name = "key";
        $GLOBALS[$name] = 4;
    } elseif ($message === "String offset cast occurred") {
        $name = "keeper";
        unset($GLOBALS[$name]);
        $name = "key";
        $GLOBALS[$name] = "not-an-offset";
    }
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$keeper = $base;
$bystander = $left . $right;
$got = 99;
$handler = $left . $right;
set_error_handler($handler, 2);
set_error_handler("requestReleaseCast");
unset($handler);
$got = $base[$key];
echo "R:", $got === null ? "null" : "other", ";B:", $base, ";K:", $key, ";S:", isset($keeper) ? "live" : "gone", ";V:", $bystander, ";Z;";
''',
    'expected_stdout': '2:Undefined variable $key;2:String offset cast occurred;R:null;B:99;K:not-an-offset;S:gone;V:abc;Z;',
    'expected_warnings': [],
    'read_line': 31,
}]
