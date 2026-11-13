"""The current or saved error callback owns the selected REQUEST string."""

CASES = [{
    'id': 'undefined-request-base-current-callback-owner',
    'source': '''<?php
function abc($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    if ($message === 'Undefined variable $key') {
        $name = "base";
        $replacement = 99;
        $GLOBALS[$name] =& $replacement;
        $name = "key";
        $GLOBALS[$name] = 0;
    }
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$got = 99;
set_error_handler($base);
$got = $base[$key];
echo "R:", $got, ";B:", $base, ";K:", $key, ";Z;";
''',
    'expected_stdout': '2:Undefined variable $key;2:String offset cast occurred;R:a;B:99;K:0;Z;',
    'expected_warnings': [],
    'read_line': 18,
}, {
    'id': 'undefined-request-base-prior-callback-owner',
    'source': '''<?php
function abc($level, $message, $file, $line) {
    return true;
}
function requestOwnerCurrent($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    if ($message === 'Undefined variable $key') {
        $name = "base";
        $replacement = 99;
        $GLOBALS[$name] =& $replacement;
        $name = "key";
        $GLOBALS[$name] = 0;
    }
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$got = 99;
set_error_handler($base, 2);
set_error_handler("requestOwnerCurrent");
$got = $base[$key];
echo "R:", $got, ";B:", $base, ";K:", $key, ";Z;";
''',
    'expected_stdout': '2:Undefined variable $key;2:String offset cast occurred;R:a;B:99;K:0;Z;',
    'expected_warnings': [],
    'read_line': 22,
}]
