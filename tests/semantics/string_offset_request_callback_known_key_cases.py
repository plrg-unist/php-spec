"""A callback owns the borrowed base while a KNOWN primitive offset stays fixed."""

CASES = [{
    'id': 'request-base-current-callback-known-false',
    'source': '''<?php
function abc($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "base";
    $replacement = 99;
    $GLOBALS[$name] =& $replacement;
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$got = 99;
set_error_handler($base);
$got = $base[false];
echo "R:", $got, ";B:", $base, ";Z;";
''',
    'expected_stdout': '2:String offset cast occurred;R:a;B:99;Z;',
    'expected_warnings': [],
    'read_line': 14,
}, {
    'id': 'request-base-prior-callback-known-true',
    'source': '''<?php
function abc($level, $message, $file, $line) {
    return true;
}
function requestKnownCast($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "base";
    $replacement = 99;
    $GLOBALS[$name] =& $replacement;
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$got = 99;
set_error_handler($base, 2);
set_error_handler("requestKnownCast");
$got = $base[true];
echo "R:", $got, ";B:", $base, ";Z;";
''',
    'expected_stdout': '2:String offset cast occurred;R:b;B:99;Z;',
    'expected_warnings': [],
    'read_line': 18,
}]
