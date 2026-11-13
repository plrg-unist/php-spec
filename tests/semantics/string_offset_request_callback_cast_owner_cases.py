"""A registered callback retains the selected header after an ordinary CAST."""

CASES = [{
    'id': 'request-base-current-callback-cast-owner',
    'source': '''<?php
function abc($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "base";
    $replacement = 99;
    $GLOBALS[$name] =& $replacement;
    $name = "key";
    $GLOBALS[$name] = 0;
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$key = false;
$got = 99;
set_error_handler($base);
$got = $base[$key];
echo "R:", $got, ";B:", $base, ";K:", $key, ";Z;";
''',
    'expected_stdout': '2:String offset cast occurred;R:a;B:99;K:0;Z;',
    'expected_warnings': [],
    'read_line': 17,
}, {
    'id': 'request-base-prior-callback-cast-owner',
    'source': '''<?php
function abc($level, $message, $file, $line) {
    return true;
}
function requestCastCurrent($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "base";
    $replacement = 99;
    $GLOBALS[$name] =& $replacement;
    $name = "key";
    $GLOBALS[$name] = 0;
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$key = false;
$got = 99;
set_error_handler($base, 2);
set_error_handler("requestCastCurrent");
$got = $base[$key];
echo "R:", $got, ";B:", $base, ";K:", $key, ";Z;";
''',
    'expected_stdout': '2:String offset cast occurred;R:a;B:99;K:0;Z;',
    'expected_warnings': [],
    'read_line': 21,
}]
