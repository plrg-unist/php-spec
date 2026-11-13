"""Observe non-NUL REQUEST release at the two initially undefined-key boundaries."""

CASES = [{
    'id': 'undefined-request-base-last-owner-release-before-cast',
    'source': '''<?php
function requestReleaseUndefined($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    if ($message === 'Undefined variable $key') {
        $name = "base";
        $replacement = 99;
        $GLOBALS[$name] =& $replacement;
        $name = "key";
        $GLOBALS[$name] = 4;
        $name = "keeper";
        unset($GLOBALS[$name]);
        restore_error_handler();
    }
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$keeper = $base;
$got = 99;
set_error_handler("requestReleaseUndefined", 2);
$got = $base[$key];
echo "R:", $got === null ? "null" : "other", ";B:", $base, ";K:", $key, ";S:", isset($keeper) ? "live" : "gone", ";Z;";
''',
    'expected_stdout': '2:Undefined variable $key;R:null;B:99;K:4;S:gone;Z;',
    'expected_warnings': [],
    'read_line': 22,
}, {
    'id': 'undefined-request-base-last-owner-release-after-cast',
    'source': '''<?php
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
        $GLOBALS[$name] = 8;
        restore_error_handler();
    }
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$keeper = $base;
$got = 99;
set_error_handler("requestReleaseCast", 2);
$got = $base[$key];
echo "R:", $got === null ? "null" : "other", ";B:", $base, ";K:", $key, ";S:", isset($keeper) ? "live" : "gone", ";Z;";
''',
    'expected_stdout': '2:Undefined variable $key;2:String offset cast occurred;R:null;B:99;K:8;S:gone;Z;',
    'expected_warnings': [],
    'read_line': 25,
}]
