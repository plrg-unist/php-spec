"""Truthy emitted string casts preserve their interned shorthand base before raw-key Warnings."""

CASES = [dict(
    id='runtime-string-cast-truthy-shorthand-base-initial-raw-leading-current-key',
    source=r'''<?php
function runtimeStringCastTruthyShorthandBaseInitialRawLeading($level, $message, $file, $line) {
    echo $level, ":", $message, ";";
    $name = "key";
    $GLOBALS[$name] = $message;
    return true;
}
$key = 0;
$got = 99;
set_error_handler("runtimeStringCastTruthyShorthandBaseInitialRawLeading");
trigger_error("1x", E_USER_WARNING);
$got = (((string)"abc") ?: "XYZ")[$key];
echo "R:", $got, ";K:", $key, ";Z;";
''',
    expected_stdout='512:1x;2:Illegal string offset "1x";R:b;K:Illegal string offset "1x";Z;',
    expected_warnings=[], read_line=12),
    dict(
    id='runtime-string-cast-truthy-shorthand-base-initial-raw-leading-reference-key',
    source=r'''<?php
function runtimeStringCastTruthyShorthandBaseInitialRawReferenceLeading($level, $message, $file, $line) {
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
set_error_handler("runtimeStringCastTruthyShorthandBaseInitialRawReferenceLeading");
trigger_error("1x", E_USER_WARNING);
$got = (((string)(string)"abc") ?: "XYZ")[$key];
echo "R:", $got, ";K:", $key, ";A:", $alias, ";Z;";
''',
    expected_stdout='512:1x;2:Illegal string offset "1x";R:b;K:2;A:Illegal string offset "1x";Z;',
    expected_warnings=[], read_line=18)]
