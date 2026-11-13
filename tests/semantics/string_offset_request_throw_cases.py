"""Keep an outside REQUEST owner when the first undefined-key handler throws."""

CASES = [{
    'id': 'undefined-request-base-supplied-throw-current-in-range',
    'source': '''<?php
function requestUndefinedThrow($level, $message, $file, $line) {
    global $supplied;
    echo "U|";
    $name = "base";
    $replacement = 99;
    $GLOBALS[$name] =& $replacement;
    $name = "key";
    $GLOBALS[$name] = 4;
    restore_error_handler();
    throw $supplied;
}
$left = "ab";
$right = "cde";
$base = $left . $right;
$keeper = $base;
$supplied = new Exception("supplied");
$dst = 99;
set_error_handler("requestUndefinedThrow", 2);
try {
    $dst = $base[$key];
    echo "bad";
} catch (Exception $caught) {
    echo $caught === $supplied ? "same|" : "other|";
    echo $dst, "|", $key, "|", $base, "|", $keeper, ";Z;";
}
''',
    'expected_stdout': 'U|same|99|4|99|abcde;Z;',
    'expected_warnings': ['String offset cast occurred'],
    'read_line': 21,
}, {
    'id': 'undefined-request-base-supplied-throw-old-bounds',
    'source': '''<?php
function requestUndefinedThrowBounds($level, $message, $file, $line) {
    global $supplied;
    echo "U|";
    $name = "base";
    $replacement = "abcdefghij";
    $GLOBALS[$name] =& $replacement;
    $name = "key";
    $GLOBALS[$name] = 8;
    restore_error_handler();
    throw $supplied;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$keeper = $base;
$supplied = new Exception("supplied");
$dst = 99;
set_error_handler("requestUndefinedThrowBounds", 2);
try {
    $dst = $base[$key];
    echo "bad";
} catch (Exception $caught) {
    echo $caught === $supplied ? "same|" : "other|";
    echo $dst, "|", $key, "|", $base, "|", $keeper, ";Z;";
}
''',
    'expected_stdout': 'U|same|99|8|abcdefghij|abc;Z;',
    'expected_warnings': ['String offset cast occurred', 'Uninitialized string offset 8'],
    'read_line': 21,
}]
