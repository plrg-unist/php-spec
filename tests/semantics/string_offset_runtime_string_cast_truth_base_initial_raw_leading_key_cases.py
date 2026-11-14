"""Quiet emitted immutable string casts select literal bases before raw-key Warnings."""

CASES = [dict(
    id='runtime-string-cast-truth-base-initial-raw-leading-current-key',
    source=r'''<?php
function runtimeStringCastTruthBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeStringCastTruthBaseInitialRawLeading");
trigger_error("1x", E_USER_WARNING);
$got = (((string)(int)"1") ? "abc" : "XYZ")[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:1x;2:Illegal string offset "1x";R:b;K:Illegal string offset "1x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-string-cast-truth-base-initial-raw-leading-reference-key',
    source=r'''<?php
function runtimeStringCastTruthBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeStringCastTruthBaseInitialRawReferenceLeading");
trigger_error("1x", E_USER_WARNING);
$got = (((string)(bool)"0") ? "XYZ" : "abc")[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:1x;2:Illegal string offset "1x";R:b;K:2;A:Illegal string offset "1x";Z;',
    expected_warnings=[], read_line=18)]
