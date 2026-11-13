"""Release with a quiet prior literal handler and the current default mask."""

CASES = [{
    'id': 'undefined-request-base-prior-handler-release-before-cast',
    'source': '''<?php
function requestReleasePrior($level, $message, $file, $line) {
    return true;
}
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
    }
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$keeper = $base;
$got = 99;
set_error_handler("requestReleasePrior", 2);
set_error_handler("requestReleaseUndefined");
$got = $base[$key];
echo "R:", $got === null ? "null" : "other", ";B:", $base, ";K:", $key, ";S:", isset($keeper) ? "live" : "gone", ";Z;";
''',
    'expected_stdout': '2:Undefined variable $key;R:null;B:99;K:4;S:gone;Z;',
    'expected_warnings': [],
    'read_line': 25,
}, {
    'id': 'undefined-request-base-prior-handler-release-after-cast',
    'source': '''<?php
function requestReleasePrior($level, $message, $file, $line) {
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
        $GLOBALS[$name] = 8;
    }
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$keeper = $base;
$got = 99;
set_error_handler("requestReleasePrior", 2);
set_error_handler("requestReleaseCast");
$got = $base[$key];
echo "R:", $got === null ? "null" : "other", ";B:", $base, ";K:", $key, ";S:", isset($keeper) ? "live" : "gone", ";Z;";
''',
    'expected_stdout': '2:Undefined variable $key;2:String offset cast occurred;R:null;B:99;K:8;S:gone;Z;',
    'expected_warnings': [],
    'read_line': 28,
}]
