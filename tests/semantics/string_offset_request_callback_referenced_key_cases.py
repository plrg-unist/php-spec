"""An initial key wrapper supplies its own current payload after CV rebinding."""
from string_offset_request_callback_rebound_key_cases import CONTROL

CASES = [dict(CONTROL), {
    'id': 'request-base-prior-callback-initial-reference-payload-two',
    'source': '''<?php
function abc($level, $message, $file, $line) {
    return true;
}
function requestReferencedKey($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "base";
    $replacementBase = 99;
    $GLOBALS[$name] =& $replacementBase;
    $name = "key";
    $replacementKey = 0;
    $GLOBALS[$name] =& $replacementKey;
    $name = "alias";
    $GLOBALS[$name] = 2;
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$key = true;
$alias =& $key;
$got = 99;
set_error_handler($base, 2);
set_error_handler("requestReferencedKey");
$got = $base[$key];
echo "R:", $got, ";B:", $base, ";K:", $key, ";A:", $alias, ";Z;";
''',
    'expected_stdout': '2:String offset cast occurred;R:c;B:99;K:0;A:2;Z;',
    'expected_warnings': [],
    'read_line': 25,
}]
