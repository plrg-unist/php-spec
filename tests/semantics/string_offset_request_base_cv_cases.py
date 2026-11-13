"""Retain a runtime base in a distinct ordinary CV through undefined-key callbacks."""

CASES = [{
    'id': 'undefined-request-base-retained-integer-rebind',
    'source': '''<?php
function requestBaseCv($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    if ($message === 'Undefined variable $missing') {
        $name = "base";
        $replacement = 99;
        $GLOBALS[$name] =& $replacement;
        $name = "missing";
        $GLOBALS[$name] = 0;
    } elseif ($message === "String offset cast occurred") {
        $name = "missing";
        $GLOBALS[$name] = 4;
    }
    return true;
}
$left = "ab";
$right = "cde";
$base = $left . $right;
$keeper = $base;
set_error_handler("requestBaseCv", 2);
echo "R:", $base[$missing], ";B:", $base, ";K:", $missing, ";S:", $keeper, ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;e;B:99;K:4;S:abcde;Z;',
    'expected_warnings': [],
    'read_line': 22,
}, {
    'id': 'undefined-request-base-retained-old-bounds',
    'source': '''<?php
function requestBaseCvBounds($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    if ($message === 'Undefined variable $missing') {
        $name = "base";
        $replacement = "abcdefghij";
        $GLOBALS[$name] =& $replacement;
        $name = "missing";
        $GLOBALS[$name] = 4;
    } elseif ($message === "String offset cast occurred") {
        $name = "missing";
        $GLOBALS[$name] = 8;
    }
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$keeper = $base;
set_error_handler("requestBaseCvBounds", 2);
echo "R:", $base[$missing], ";B:", $base, ";K:", $missing, ";S:", $keeper, ";Z;";
''',
    'expected_stdout': 'R:2:Undefined variable $missing;2:String offset cast occurred;2:Uninitialized string offset 8;;B:abcdefghij;K:8;S:abc;Z;',
    'expected_warnings': [],
    'read_line': 22,
}]
