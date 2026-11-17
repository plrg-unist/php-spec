"""One-byte emitted string bitwise bases survive initial raw-key Warnings."""

CASES = [dict(
    id='runtime-string-bitwise-base-initial-raw-leading-current-key',
    source=r'''<?php
function runtimeStringBitwiseBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeStringBitwiseBaseInitialRawLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((string)"c") & "b")[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-string-bitwise-base-initial-raw-leading-reference-key',
    source=r'''<?php
function runtimeStringBitwiseBaseInitialRawReferenceLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "alias";
    $GLOBALS[$name] = $message;
    if ($level === E_WARNING) {
        $name = "key";
        $replacementKey = 2;
        $GLOBALS[$name] =& $replacementKey;
    }
    return true;
}
$key = 0;
$alias =& $key;
$got = 99;
set_error_handler("runtimeStringBitwiseBaseInitialRawReferenceLeading");
trigger_error("0x", E_USER_WARNING);
$got = (((string)"3") ^ (((string)"P") | "Q"))[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:0x;2:Illegal string offset "0x";R:b;K:2;A:Illegal string offset "0x";Z;',
    expected_warnings=[], read_line=18)]
