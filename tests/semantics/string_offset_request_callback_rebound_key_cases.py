"""A selected callback keeps old bytes while the CV key moves to a fresh reference."""

CASES = [{
    'id': 'request-base-current-callback-rebound-key-two',
    'source': '''<?php
function abc($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "base";
    $replacementBase = 99;
    $GLOBALS[$name] =& $replacementBase;
    $name = "key";
    $replacementKey = 2;
    $GLOBALS[$name] =& $replacementKey;
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
    'expected_stdout': '2:String offset cast occurred;R:c;B:99;K:2;Z;',
    'expected_warnings': [],
    'read_line': 18,
}, {
    'id': 'request-base-prior-callback-rebound-key-zero',
    'source': '''<?php
function abc($level, $message, $file, $line) {
    return true;
}
function requestReboundKey($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "base";
    $replacementBase = 99;
    $GLOBALS[$name] =& $replacementBase;
    $name = "key";
    $replacementKey = 0;
    $GLOBALS[$name] =& $replacementKey;
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$key = true;
$got = 99;
set_error_handler($base, 2);
set_error_handler("requestReboundKey");
$got = $base[$key];
echo "R:", $got, ";B:", $base, ";K:", $key, ";Z;";
''',
    'expected_stdout': '2:String offset cast occurred;R:a;B:99;K:0;Z;',
    'expected_warnings': [],
    'read_line': 22,
}]
