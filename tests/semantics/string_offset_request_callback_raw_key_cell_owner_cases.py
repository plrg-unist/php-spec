"""Real ordinary cells retain a selected REQUEST base after callback-owner loss."""

CASES = [dict(
    id='request-callback-raw-key-current-base-owner',
    source='''<?php
function abc($level, $message, $file, $line) {
    return true;
}
function requestRawCellOwner($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    restore_error_handler();
    restore_error_handler();
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$key = true;
$got = 99;
set_error_handler($base, 2);
set_error_handler("requestRawCellOwner");
$got = $base[$key];
echo "R:", $got, ";B:", $base, ";K:", $key, ";Z;";
''',
    expected_stdout='2:String offset cast occurred;R:a;B:abc;K:String offset cast occurred;Z;',
    expected_warnings=[], read_line=20),
    dict(
    id='request-callback-raw-key-distinct-base-owner',
    source='''<?php
function abc($level, $message, $file, $line) {
    return true;
}
function requestRawCellOwner($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "base";
    $replacementBase = 99;
    $GLOBALS[$name] =& $replacementBase;
    $name = "key";
    $GLOBALS[$name] = $message;
    restore_error_handler();
    restore_error_handler();
    return true;
}
$left = "a";
$right = "bc";
$base = $left . $right;
$keeper = $base;
$key = true;
$got = 99;
set_error_handler($base, 2);
set_error_handler("requestRawCellOwner");
$got = $base[$key];
echo "R:", $got, ";B:", $base, ";K:", $key, ";P:", $keeper, ";Z;";
''',
    expected_stdout='2:String offset cast occurred;R:a;B:99;K:String offset cast occurred;P:abc;Z;',
    expected_warnings=[], read_line=24)]
