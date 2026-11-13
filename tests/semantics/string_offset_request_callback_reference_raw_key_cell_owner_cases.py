"""Initial key wrappers retain raw payloads after selected callback-owner loss."""

CASES = [dict(
    id='request-callback-reference-raw-key-current-base-owner',
    source='''<?php
function abc($level, $message, $file, $line) {
    return true;
}
function requestRawInitialOwner($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "alias";
    $GLOBALS[$name] = $message;
    $name = "key";
    $replacementKey = 2;
    $GLOBALS[$name] =& $replacementKey;
    restore_error_handler();
    restore_error_handler();
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$key = true;
$alias =& $key;
$got = 99;
set_error_handler($base, 2);
set_error_handler("requestRawInitialOwner");
$got = $base[$key];
echo "R:", $got, ";B:", $base, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='2:String offset cast occurred;R:a;B:abc;K:2;A:String offset cast occurred;Z;',
    expected_warnings=[], read_line=24),
    dict(
    id='request-callback-reference-raw-key-distinct-base-owner',
    source='''<?php
function abc($level, $message, $file, $line) {
    return true;
}
function requestRawInitialOwner($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "base";
    $replacementBase = 99;
    $GLOBALS[$name] =& $replacementBase;
    $name = "alias";
    $GLOBALS[$name] = $message;
    $name = "key";
    unset($GLOBALS[$name]);
    restore_error_handler();
    restore_error_handler();
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$keeper = $base;
$key = true;
$alias =& $key;
$got = 99;
set_error_handler($base, 2);
set_error_handler("requestRawInitialOwner");
$got = $base[$key];
echo "R:", $got, ";B:", $base, ";K:", isset($key), ";P:", $keeper, ";A:", $alias, ";Z;";
''',
    expected_stdout='2:String offset cast occurred;R:a;B:99;K:;P:abc;A:String offset cast occurred;Z;',
    expected_warnings=[], read_line=27)]
